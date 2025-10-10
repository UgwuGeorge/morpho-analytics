from __future__ import annotations

from pathlib import Path
import json
import numpy as np

from morpho_analytics.track import track, metrics, save_overlay_png


def main() -> None:
    here = Path(__file__).parent
    # Placeholder raster-like synthetic: static hotspots appearing over time
    T, H, W = 15, 128, 128
    series = np.zeros((T, H, W), dtype=np.float32)
    rng = np.random.default_rng(42)
    centers = [(32, 40), (80, 70), (96, 24)]
    radii = [8.0, 10.0, 6.0]
    ys, xs = np.mgrid[0:H, 0:W]
    for t in range(T):
        arr = np.zeros((H, W), dtype=np.float32)
        for (cy, cx), r in zip(centers, radii):
            rr = r * (1.0 + 0.1 * np.sin(2 * np.pi * (t / 6.0)))
            d2 = (xs - cx) ** 2 + (ys - cy) ** 2
            arr += np.exp(-d2 / (2.0 * (rr ** 2)))
        arr += 0.05 * rng.standard_normal((H, W)).astype(np.float32)
        arr -= arr.min()
        m = arr.max()
        if m > 0:
            arr /= m
        series[t] = arr

    tr = track(series)
    res = metrics(tr)
    (here / "geo_report.json").write_text(json.dumps(res, indent=2))
    save_overlay_png(series, tr.labels, str(here / "geo_overlay.png"))
    print("OK: geo_report.json + geo_overlay.png written")


if __name__ == "__main__":
    main()
