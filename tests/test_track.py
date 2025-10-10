from __future__ import annotations

import os
import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

TESTS_DIR = Path(__file__).resolve().parent
SRC_PATH = TESTS_DIR.parent / "src" / "morpho_analytics"

TRACK_SPEC = spec_from_file_location("morpho_analytics.track", SRC_PATH / "track.py")
if TRACK_SPEC is None or TRACK_SPEC.loader is None:
    raise ImportError("Impossible de charger morpho_analytics.track depuis le squelette local")
track_module = module_from_spec(TRACK_SPEC)
sys.modules[TRACK_SPEC.name] = track_module
TRACK_SPEC.loader.exec_module(track_module)

track = track_module.track
metrics = track_module.metrics
save_overlay_png = track_module.save_overlay_png


def _make_synth(T: int = 5, H: int = 64, W: int = 64, r: float = 6.0) -> np.ndarray:
    ys, xs = np.mgrid[0:H, 0:W]
    series = np.zeros((T, H, W), dtype=np.float32)
    cx0, cy0, vx, vy = 10.0, 8.0, 2.0, 1.0
    for t in range(T):
        cx, cy = cx0 + vx * t, cy0 + vy * t
        d2 = (xs - cx) ** 2 + (ys - cy) ** 2
        series[t] = np.exp(-d2 / (2.0 * (r**2)))
    series -= series.min()
    m = series.max()
    if m > 0:
        series /= m
    return series.astype(np.float32)


class TestMorphoAnalytics(unittest.TestCase):
    def test_track_and_metrics(self) -> None:
        series = _make_synth(T=5)
        tr = track(series, threshold=None, connectivity=4, min_area=1)
        self.assertEqual(len(tr.labels), series.shape[0])

        res = metrics(tr)
        for key in {"area_mean", "area_max", "duration", "events"}:
            self.assertIn(key, res)
        self.assertEqual(res["duration"], series.shape[0])
        self.assertEqual(len(res["events"]), series.shape[0])

    def test_save_overlay_png(self) -> None:
        series = _make_synth(T=3)
        tr = track(series, threshold=None, connectivity=4, min_area=1)

        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            save_overlay_png(series, tr.labels, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
