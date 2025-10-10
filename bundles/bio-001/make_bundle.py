from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from morpho_analytics.track import metrics, save_overlay_png, track


def make_synth_series(T: int = 20, H: int = 128, W: int = 128, r: int = 10) -> np.ndarray:
    """Reproduce the synthetic demo series (moving blob)."""
    series = np.zeros((T, H, W), dtype=np.float32)
    ys, xs = np.mgrid[0:H, 0:W]
    cx0, cy0 = 20.0, 20.0
    vx, vy = 3.0, 2.0
    for t in range(T):
        cx = cx0 + vx * t
        cy = cy0 + vy * t
        d2 = (xs - cx) ** 2 + (ys - cy) ** 2
        series[t] = np.exp(-d2 / (2.0 * (r**2)))
    series -= series.min()
    m = series.max()
    if m > 0:
        series /= m
    return series.astype(np.float32)


def main() -> None:
    here = Path(__file__).parent
    synth_path = here / "synth.npy"
    report_json = here / "report.json"
    report_png = here / "report.png"

    print("[bio-001] Generating synthetic series…")
    series = make_synth_series()
    np.save(synth_path, series)
    print(f"[bio-001] Saved {synth_path.relative_to(here)} with shape {series.shape}")

    print("[bio-001] Running tracking…")
    tracks = track(series, threshold=None, connectivity=4, min_area=5)
    report = metrics(tracks)
    report_json.write_text(json.dumps(report, indent=2))
    print(f"[bio-001] Saved {report_json.relative_to(here)}")

    print("[bio-001] Rendering overlay…")
    save_overlay_png(series, tracks.labels, str(report_png))
    print(f"[bio-001] Saved {report_png.relative_to(here)}")
    print("[bio-001] Bundle generation complete.")


if __name__ == "__main__":
    main()
