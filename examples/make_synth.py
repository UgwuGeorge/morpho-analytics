from __future__ import annotations

from pathlib import Path

import numpy as np


def make_synth(T: int = 20, H: int = 128, W: int = 128, r: int = 10) -> np.ndarray:
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


if __name__ == "__main__":
    out = Path(__file__).with_name("synth.npy")
    arr = make_synth()
    np.save(out, arr)
    print(f"Wrote {out} with shape {arr.shape}")
