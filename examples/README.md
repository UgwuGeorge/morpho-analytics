# Examples

Suggested notebooks (to add):
- Game of Life (synthetic) → island tracking + metrics.
- Open geospatial raster → hot-spot detection/tracking.

Provided notebooks
- `bio_synthetic_tracking.ipynb`
- `geo_raster_tracking.ipynb`

Demo CLI input format
- Generate a synthetic series: `python examples/make_synth.py` → `examples/synth.npy`.
- Run locally (venv): `morphoctl report examples/synth.npy --out examples/report.json --fig examples/report.png`
- Via Docker: `docker build -t morpho-analytics . && docker run --rm -v "$PWD/examples":/data morpho-analytics report /data/synth.npy --out /data/report.json --fig /data/report.png`

Notebook-equivalent scripts (avoid editing .ipynb)
- `examples/bio_synthetic_tracking.py` — generates/loads `synth.npy`, produces `bio_report.json` + `bio_overlay.png`.
- `examples/geo_raster_tracking.py` — synthetic raster series, produces `geo_report.json` + `geo_overlay.png`.
- Check CLI version: `morphoctl --version`
