# fiesta-galaxy-cellprofiler-eo

> **Galaxy bioimaging tools, applied cross-discipline to Earth Observation.**
>
> Part of OSCARS-FIESTA. Reuses the GTN tutorial *"Object tracking using CellProfiler"* ([`gxy.io/GTN:T00516`](https://gxy.io/GTN:T00516)) and the CellProfiler software ([Carpenter et al. 2006](https://doi.org/10.1186/gb-2006-7-10-r100)).

CellProfiler's `TrackObjects` module — built to follow **dividing nuclei** in fluorescence time-lapse microscopy — is run **unchanged** through a Galaxy workflow on **usegalaxy.eu** (Galaxy Europe) to track **drifting icebergs** across a NASA MODIS satellite time-series (iceberg A-68A past South Georgia, 2020–2021). Bright bergs on a dark ocean are the Earth-observation mirror of bright nuclei on a dark background, and a **calving** berg (one object splitting into two) is the mirror of a dividing nucleus. This repository produces:

- A reproducible pipeline (Snakefile + notebooks), runnable on Galaxy or via a same-algorithm local fallback.
- A Science Live nanopublication chain documenting the claim, method, and outcome with provenance.
- A Zenodo-archived release (source + container image) with a citable DOI.

## Quick start

```bash
git clone https://github.com/annefou/fiesta-galaxy-cellprofiler-eo.git
cd fiesta-galaxy-cellprofiler-eo
pixi install
pixi run snakemake --cores 1
```

Or with Docker:

```bash
docker run --rm ghcr.io/annefou/fiesta-galaxy-cellprofiler-eo:latest
```

## Two ways to run

- **Galaxy (showcased):** runs `workflow/main_workflow.ga` on **usegalaxy.eu** via BioBlend. **Requires a usegalaxy.eu API key** at `~/.galaxy_eu_key`.
- **Local fallback (CI / hermetic):** the *same algorithm* offline (skimage Otsu segmentation + frame-to-frame overlap tracking) — no key needed.

## Structure

- `notebooks/` — jupytext `.py` notebooks that drive the pipeline.
- `workflow/main_workflow.ga` — the Galaxy CellProfiler tracking workflow.
- `data/` — downloaded by `notebooks/01_data_download.py`, never committed.
- `nanopubs/` — drafts of the FORRT chain field-by-field, plus the published-URI registry.
- `figures/` — curated figures used in the Jupyter Book.

## Nanopublication chain

The FORRT chain for this work is registered in [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md) (publish on the Science Live platform and paste URIs there).
