# Morpho-Analytics

*Watch the demo (link to be added)*

![HeLa Demo GIF](docs/media/demo-hela.gif)

An advanced, Docker-ready command-line tool for object tracking and morpho-dynamic analysis in image sequences. Go from raw image series to actionable data with a single, reproducible command.

---

## What It Does

Morpho-Analytics applies a fast, deterministic intensity-thresholding algorithm to detect and track structures over time. It is designed for researchers and engineers who need reliable, scriptable analysis without the overhead of complex deep learning stacks or GUIs.

## Quickstart with Docker

Get your first result in minutes. The following command runs the analysis on a built-in synthetic dataset. Ensure you are in a directory containing an `examples` folder.

```bash
docker run --rm -v "$PWD/examples":/data eliotsystem/morpho-analytics:v0.1.9 report /data/synth.npy --out /data/report.json --fig /data/report.png
```
*Note: `:latest` can be used as an alternative to `:v0.1.9`.*

## Detailed Output Formats

The tool provides rich, machine-readable outputs ready for scientific analysis.

*   **JSON Records (default):** A detailed log of every detected object per frame.

    *Excerpt from a `report.json` file:*
    ```json
    [
      {
        "t": 12,
        "label": 5,
        "area": 1432,
        "centroid-0": 301.4,
        "centroid-1": 212.7,
        "mean_intensity": 0.47,
        "max_intensity": 0.93
      }
    ]
    ```

*   **CSV Format:** Get the same detailed report in CSV format by adding the `--format csv` flag.

*   **Optional Summary:** Generate a simple summary file (with `area_mean`, `duration`, etc.) by adding the `--summary-out summary.json` flag.

## HeLa Cell Tracking Demo

This tool was tested on the DIC-C2DH-HeLa dataset from the Cell Tracking Challenge.

1.  **Convert TIFFs to NPY:**
    ```bash
    python marketing/demo-assets/make_npy_from_tiffs.py --input DIC-C2DH-HeLa/01 --output hela_series.npy
    ```
2.  **Run Docker Analysis:**
    ```bash
    docker run --rm -v "$PWD":/data eliotsystem/morpho-analytics:v0.1.9 report /data/hela_series.npy --out /data/report.json --fig /data/report.png
    ```

## Visuals

The analysis also produces visual outputs for quick validation.

**Object Centroids Over Time:**
![Object Centroids Plot](docs/media/centroids_hela.png)

## License

This software is provided "as-is" with no support, for R&D use only. See the full [EULA.md](EULA.md) for details.

*Dataset Credit: The HeLa cell images are from the Cell Tracking Challenge, sponsored by ISS, CTB, and NIH.*