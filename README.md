# Morpho-Analytics

**From data to proof in 30 seconds**  
A Docker-ready command-line tool for object tracking and morpho-dynamic analysis on image sequences.

---

## 🎬 Demo Animation

![demo](docs/media/demo-hela.gif)  
*(This GIF illustrates the transformation: command → visual result + metrics.)*

---

## Proofs & Visual Validation

### Overlay proof (red overlay on image)  
![overlay proof](docs/media/overlay_hela.png)

### Centroids over time (object positions across frames)  
![centroids over time](docs/media/report.png)

---

## Quickstart with Docker

Run the analysis in minutes from the root of the project:

```bash
docker run --rm -v "$PWD/examples":/data eliotsystem/morpho-analytics:v0.1.9 report /data/synth.npy --out /data/report.json --fig /data/report.png
```

### From Quickstart to Results (copy/paste)

If you just want a minimal, copy‑paste path from the Quickstart to seeing files appear:

1) Be in the project root so that `examples/` exists:

```
cd /path/to/morpho-analytics
```

2) Run the command (identical to Quickstart):

```
docker run --rm -v "$PWD/examples":/data \
  eliotsystem/morpho-analytics:v0.1.9 \
  report /data/synth.npy --out /data/report.json --fig /data/report.png
```

3) Verify the outputs were created next to the input:

```
ls -lh examples/report.json examples/report.png
```

4) (Optional) Peek the first lines of the JSON records:

```
sed -n '1,10p' examples/report.json
```

Notes
- The `-v "$PWD/examples":/data` mount means the container sees your local `examples/` as `/data`. Always pass `/data/<file>` to the CLI, not `examples/<file>`.
- Filenames are case‑sensitive on Linux.
- Pinning `:v0.1.9` ensures reproducibility; `:latest` is available once CI finishes.
