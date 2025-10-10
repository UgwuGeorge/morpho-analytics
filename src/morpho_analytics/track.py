"""Minimal API skeleton for morpho-dynamic tracking (no TDS deps).

Stub functions:
- segment: optional preprocessing/segmentation
- label: connected-component labeling
- track: frame-to-frame associations (birth/death/merge/split)
- metrics: simple metrics (area, duration, events)

These functions return minimal structures to unblock notebooks/CLI
before the full implementation is delivered.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Sequence
import numpy as np


@dataclass
class Tracks:
    labels: List[np.ndarray]
    events: List[Dict[str, Any]]


def segment(frame: np.ndarray, *, threshold: float | None = None) -> np.ndarray:
    """Return a trivial binary mask (skeleton placeholder)."""
    if threshold is None:
        threshold = float(np.nanmean(frame))
    return (frame >= threshold).astype(np.uint8)


def label(mask: np.ndarray, *, connectivity: int = 4) -> np.ndarray:
    """Return a labeled image (placeholder: binary => {0,1})."""
    return (mask > 0).astype(np.int32)


def track(series: np.ndarray, *, threshold: float | None = None, connectivity: int = 4, min_area: int = 5) -> Tracks:
    """Trivially associates labels across frames (placeholder)."""
    labels: List[np.ndarray] = []
    events: List[Dict[str, Any]] = []
    for t in range(series.shape[0]):
        mask = segment(series[t], threshold=threshold)
        lab = label(mask, connectivity=connectivity)
        if min_area > 1:
            # Naive filter: drop tiny components (placeholder)
            lab = lab * (np.sum(lab > 0) >= min_area)
        labels.append(lab)
        events.append({"t": t, "births": 0, "deaths": 0, "merge": 0, "split": 0})
    return Tracks(labels=labels, events=events)


def metrics(tracks: Tracks, features: Tuple[str, ...] = ("area", "duration", "events")) -> Dict[str, Any]:
    """Return bare-minimum metrics for stub tests/reports."""
    areas = [int(np.sum(lab > 0)) for lab in tracks.labels]
    duration = len(tracks.labels)
    return {
        "area_mean": float(np.mean(areas)) if areas else 0.0,
        "area_max": int(np.max(areas)) if areas else 0,
        "duration": duration,
        "events": tracks.events,
    }


def render_overlay(series: np.ndarray, labels: Sequence[np.ndarray], *, t: int | str = "last", alpha: float = 0.4) -> "Image.Image":
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

    # defensive clamping
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

    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def save_overlay_png(series: np.ndarray, labels: Sequence[np.ndarray], out_path: str, *, t: int | str = "last", alpha: float = 0.4) -> None:
    """Persist an overlay PNG built from a series and its labels."""
    img = render_overlay(series, labels, t=t, alpha=alpha)
    img.save(out_path)
