from __future__ import annotations

from pathlib import Path
import json
import numpy as np

from morpho_analytics.track import track, metrics, save_overlay_png


def main() -> None:
    here = Path(__file__).parent
    synth = here / "synth.npy"
    if not synth.exists():
        # Fallback: generate a tiny synthetic blob sequence
        T, H, W, r = 20, 128, 128, 10.0
        ys, xs = np.mgrid[0:H, 0:W]
        series = np.zeros((T, H, W), dtype=np.float32)
        cx0, cy0, vx, vy = 20.0, 20.0, 3.0, 2.0
        for t in range(T):
            cx, cy = cx0 + vx * t, cy0 + vy * t
            d2 = (xs - cx) ** 2 + (ys - cy) ** 2
            series[t] = np.exp(-d2 / (2.0 * (r ** 2)))
        series -= series.min()
        m = series.max()
        if m > 0:
            series /= m
        np.save(synth, series.astype(np.float32))

    series = np.load(synth, allow_pickle=False)
    tr = track(series)
    res = metrics(tr)
    (here / "bio_report.json").write_text(json.dumps(res, indent=2))
    save_overlay_png(series, tr.labels, str(here / "bio_overlay.png"))
    print("OK: bio_report.json + bio_overlay.png written")


if __name__ == "__main__":
    main()
