from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import numpy as np

from . import __version__ as VERSION
from .track import (
    track_objects,
    save_report,
    get_metrics,
    save_overlay_png,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="morphoctl",
        description="Morpho-Analytics CLI",
        epilog=(
            "Examples:\n"
            "  morphoctl report examples/synth.npy --out examples/report.json --fig examples/report.png\n"
            "  morphoctl report examples/synth.npy --out examples/report.csv --format csv --summary-out examples/summary.json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rep = sub.add_parser("report", help="Generate a detailed report (JSON records or CSV) from a .npy time-series")
    rep.add_argument("series", type=Path, help="Path to .npy file (T,H,W)")
    rep.add_argument("--out", type=Path, default=Path("report.json"), help="Detailed report path (JSON or CSV)")
    rep.add_argument("--format", type=str, default="json", help="Report format: 'json' (default) or 'csv'")
    rep.add_argument("--summary-out", type=Path, default=None, help="Optional summary JSON path (aggregates)")
    rep.add_argument("--threshold", type=float, default=0.5)
    rep.add_argument("--connectivity", type=int, default=4)
    rep.add_argument("--min_area", type=int, default=10)
    rep.add_argument("--fig", type=Path, default=Path("report.png"), help="Quick-look PNG figure path")
    rep.add_argument("--fig_t", default="last", help="Time index for overlay (int or 'last')")
    rep.add_argument("--alpha", type=float, default=0.4, help="Overlay alpha [0..1]")

    args = parser.parse_args()

    if args.cmd == "report":
        if not args.series.exists():
            print(f"Series not found: {args.series}", file=sys.stderr)
            sys.exit(2)
        try:
            series = np.load(args.series, allow_pickle=False)
        except Exception as e:
            print(f"Failed to read .npy: {e}", file=sys.stderr)
            sys.exit(2)

        if not isinstance(series, np.ndarray) or series.ndim != 3:
            print("Expected NumPy array shaped (T,H,W)", file=sys.stderr)
            sys.exit(2)
        if min(series.shape) <= 0:
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

        df = track_objects(series, threshold=args.threshold, connectivity=args.connectivity, min_area=args.min_area)
        save_report(df, str(args.out), str(args.fig), fmt=args.format)
        if args.summary_out is not None:
            summary = get_metrics(df)
            Path(args.summary_out).write_text(json.dumps(summary, indent=2))
        print(f"OK: detailed report {args.out} + figure {args.fig}")


if __name__ == "__main__":
    main()
