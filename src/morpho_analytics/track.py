from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.measure import label as sk_label, regionprops_table


@dataclass
class Tracks:
    labels: List[np.ndarray]
    events: List[Dict[str, Any]]


def segment(frame: np.ndarray, *, threshold: float | None = None) -> np.ndarray:
    """Return a binary mask using a simple threshold (placeholder)."""
    if threshold is None:
        threshold = float(np.nanmean(frame))
    return (frame >= threshold).astype(np.uint8)


def label(mask: np.ndarray, *, connectivity: int = 4) -> np.ndarray:
    """Return labeled components for a binary mask."""
    return sk_label(mask, connectivity=connectivity)


def track(
    series: np.ndarray,
    *,
    threshold: float | None = None,
    connectivity: int = 4,
    min_area: int = 5,
) -> Tracks:
    """Trivially associates labels frame-by-frame (placeholder)."""
    labels: List[np.ndarray] = []
    events: List[Dict[str, Any]] = []
    for t in range(series.shape[0]):
        mask = segment(series[t], threshold=threshold)
        lab = label(mask, connectivity=connectivity)
        if min_area > 1:
            keep = np.where(lab > 0, 1, 0)
            if int(np.sum(keep)) < min_area:
                lab = np.zeros_like(lab)
        labels.append(lab)
        events.append({"t": t, "births": 0, "deaths": 0, "merge": 0, "split": 0})
    return Tracks(labels=labels, events=events)


def metrics(tracks: Tracks, features: Tuple[str, ...] = ("area", "duration", "events")) -> Dict[str, Any]:
    """Return minimal metrics for stub use-cases."""
    areas = [int(np.sum(lab > 0)) for lab in tracks.labels]
    duration = len(tracks.labels)
    return {
        "area_mean": float(np.mean(areas)) if areas else 0.0,
        "area_max": int(np.max(areas)) if areas else 0,
        "duration": duration,
        "events": tracks.events,
    }


def render_overlay(
    series: np.ndarray,
    labels: Sequence[np.ndarray],
    *,
    t: int | str = "last",
    alpha: float = 0.4,
) -> "Image.Image":
    """Build a simple overlay image (grayscale + labels in red)."""
    try:
        from PIL import Image  # type: ignore
    except Exception as e:  # pragma: no cover - missing dependency
        raise RuntimeError("Pillow is required to export PNG images (pip install Pillow).") from e

    if len(labels) == 0:
        raise ValueError("No labels provided for overlay rendering.")

    t_idx = len(labels) - 1 if t == "last" else int(t)
    if t_idx < 0 or t_idx >= len(labels):
        raise IndexError(f"Invalid time index {t_idx} for overlay (length={len(labels)}).")

    frame = series[t_idx].astype(np.float32)
    lab = labels[t_idx]
    if frame.shape != lab.shape:
        raise ValueError(f"Shape mismatch: frame{frame.shape} vs label{lab.shape}")

    try:
        import numpy as _np  # type: ignore

        alpha = float(_np.clip(alpha, 0.0, 1.0))
    except Exception:
        alpha = float(alpha)

    vmin = float(np.nanmin(frame))
    vmax = float(np.nanmax(frame))
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax <= vmin:
        gray = np.zeros_like(frame, dtype=np.uint8)
    else:
        norm = (frame - vmin) / (vmax - vmin)
        gray = (np.clip(norm, 0.0, 1.0) * 255.0).astype(np.uint8)

    rgb = np.stack([gray, gray, gray], axis=-1).astype(np.float32)
    mask = lab > 0
    if mask.any():
        overlay = np.zeros_like(rgb)
        overlay[..., 0] = 255.0
        rgb[mask] = (1.0 - alpha) * rgb[mask] + alpha * overlay[mask]

    from PIL import Image  # type: ignore

    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def save_overlay_png(
    series: np.ndarray,
    labels: Sequence[np.ndarray],
    out_path: str,
    *,
    t: int | str = "last",
    alpha: float = 0.4,
) -> None:
    """Persist an overlay PNG built from a series and its labels."""
    img = render_overlay(series, labels, t=t, alpha=alpha)
    img.save(out_path)


def _normalize_connectivity(user_conn: int | None, ndim: int) -> int:
    """Map common pixel connectivities to skimage rank (2D: 4->1, 8->2)."""
    if user_conn is None:
        return 1
    try:
        uc = int(user_conn)
    except Exception:
        return 1
    if ndim == 2:
        return 1 if uc <= 4 else 2
    if ndim == 3:
        if uc <= 6:
            return 1
        elif uc <= 18:
            return 2
        else:
            return 3
    return max(1, min(ndim, uc))


def track_objects(series: np.ndarray, threshold: float = 0.5, connectivity: int = 4, min_area: int = 10) -> pd.DataFrame:
    """Extract detections frame-by-frame and return a detailed DataFrame."""
    all_props: List[pd.DataFrame] = []
    for t, frame in enumerate(series):
        binary_mask = frame > threshold
        conn = _normalize_connectivity(connectivity, ndim=2)
        labeled_mask = sk_label(binary_mask, connectivity=conn)

        props = regionprops_table(
            labeled_mask,
            intensity_image=frame,
            properties=("label", "area", "centroid", "max_intensity", "mean_intensity"),
        )

        df_props = pd.DataFrame(props)
        df_props = df_props[df_props["area"] >= min_area]

        if not df_props.empty:
            df_props["t"] = t
            all_props.append(df_props)

    if not all_props:
        return pd.DataFrame()

    return pd.concat(all_props, ignore_index=True)


def get_metrics(df: pd.DataFrame) -> dict:
    """Calculate useful aggregated metrics from the detailed detections."""
    if df.empty:
        return {
            "object_count": 0,
            "total_detections": 0,
            "duration": 0,
            "area_mean": 0,
            "area_max": 0,
        }

    duration = int(df["t"].max() + 1) if "t" in df.columns else 0
    object_counts = df.groupby("t")["label"].nunique()
    mean_objects = float(object_counts.mean()) if not object_counts.empty else 0.0

    return {
        "object_count": int(round(mean_objects)),
        "total_detections": int(len(df)),
        "duration": duration,
        "area_mean": float(df["area"].mean()),
        "area_max": int(df["area"].max()),
    }


def save_report(df: pd.DataFrame, out_path: str, fig_path: str, fmt: str = "json") -> None:
    """Save the detailed detections to disk and render a quick-look figure."""
    if fmt == "json":
        df.to_json(out_path, orient="records", indent=2)
    elif fmt == "csv":
        df.to_csv(out_path, index=False)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Choose 'json' or 'csv'.")

    if df.empty:
        # still generate an empty placeholder figure to avoid surprises
        plt.figure(figsize=(4, 4))
        plt.title("No detections")
        plt.savefig(fig_path)
        plt.close()
        return

    plt.figure(figsize=(6, 6))
    plt.scatter(df["centroid-1"], df["centroid-0"], c=df["t"], cmap="viridis", s=5)
    plt.title("Object Centroids Over Time")
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.gca().invert_yaxis()
    plt.colorbar(label="Time (frame)")
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()
