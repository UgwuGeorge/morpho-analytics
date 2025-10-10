from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import numpy as np

from . import __version__ as VERSION
from .track import track, metrics, save_overlay_png


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="morphoctl",
        description="Morpho-Analytics CLI",
        epilog=(
            "Examples:\n"
            "  morphoctl report examples/synth.npy --out examples/report.json --fig examples/report.png\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rep = sub.add_parser("report", help="Generate a minimal JSON report from a .npy time-series")
    rep.add_argument("series", help="Path to .npy file (T,H,W)")
    rep.add_argument("--out", default="report.json")
    rep.add_argument("--threshold", type=float, default=None)
    rep.add_argument("--connectivity", type=int, default=4)
    rep.add_argument("--min_area", type=int, default=5)
    rep.add_argument("--fig", default=None, help="Overlay PNG path (optional)")
    rep.add_argument("--fig_t", default="last", help="Time index for overlay (int or 'last')")
    rep.add_argument("--alpha", type=float, default=0.4, help="Overlay alpha [0..1]")

    args = parser.parse_args()

    if args.cmd == "report":
        path = Path(args.series)
        if not path.exists():
            print(f"Series not found: {path}", file=sys.stderr)
            sys.exit(2)
        try:
            series = np.load(path, allow_pickle=False)
        except Exception as e:
            print(f"Failed to read .npy: {e}", file=sys.stderr)
            sys.exit(2)

        if not isinstance(series, np.ndarray) or series.ndim != 3:
            print("Expected NumPy array shaped (T,H,W)", file=sys.stderr)
            sys.exit(2)
        if series.shape[0] <= 0 or series.shape[1] <= 0 or series.shape[2] <= 0:
            print("Invalid dimensions: (T,H,W) must be > 0", file=sys.stderr)
            sys.exit(2)

        if not (0.0 <= args.alpha <= 1.0):
            print("--alpha must be in [0,1]", file=sys.stderr)
            sys.exit(2)
        if args.fig and args.fig_t != "last":
            try:
                _ = int(args.fig_t)
            except Exception:
                print("--fig_t must be an integer or 'last'", file=sys.stderr)
                sys.exit(2)
        tr = track(series, threshold=args.threshold, connectivity=args.connectivity, min_area=args.min_area)
        res = metrics(tr)
        out = Path(args.out)
        out.write_text(json.dumps(res, indent=2))

        if args.fig:
            save_overlay_png(series, tr.labels, args.fig, t=args.fig_t, alpha=args.alpha)
            print(f"OK: JSON report {out} + PNG {args.fig}")
        else:
            print(f"OK: report written to {out}")


if __name__ == "__main__":
    main()
