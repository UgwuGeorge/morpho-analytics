# FAQ — Morpho-Analytics

- What does the CLI output?
  - JSON report (area_mean, area_max, duration, events) and optional PNG overlay.
- Quickstart?
  - `docker run --rm -v "$PWD/examples":/data eliotsystem/morpho-analytics:latest report /data/synth.npy --out /data/report.json --fig /data/report.png`
- Any dependencies required locally?
  - Docker only. For local Python dev, see README and `pip freeze > SBOM.txt`.
- Support/SLA?
  - As‑is/no‑support (see EULA). Community issues only, best‑effort.
- Licensing?
  - Annual commercial “as‑is”. See EULA.md.

