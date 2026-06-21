# fiesta-galaxy-cellprofiler-eo

[![CI](https://github.com/annefou/fiesta-galaxy-cellprofiler-eo/actions/workflows/ci.yml/badge.svg)](https://github.com/annefou/fiesta-galaxy-cellprofiler-eo/actions/workflows/ci.yml)
[![Jupyter Book](https://github.com/annefou/fiesta-galaxy-cellprofiler-eo/actions/workflows/jupyter-book.yml/badge.svg)](https://annefou.github.io/fiesta-galaxy-cellprofiler-eo/)
[![Docker](https://github.com/annefou/fiesta-galaxy-cellprofiler-eo/actions/workflows/docker.yml/badge.svg)](https://github.com/annefou/fiesta-galaxy-cellprofiler-eo/pkgs/container/fiesta-galaxy-cellprofiler-eo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FAIR4RS](https://img.shields.io/badge/FAIR4RS-conformant-brightgreen)](docs/fair4rs-checklist.md)
[![FORRT](https://img.shields.io/badge/FORRT-replication-blue)](https://forrt.org/)
[![Science Live](https://img.shields.io/badge/Science%20Live-nanopub%20chain-purple)](nanopubs/PUBLISHED.md)
[![RO-Crate](https://img.shields.io/badge/RO--Crate-1.2-orange)](ro-crate-metadata.json)

> **A bioimaging object tracker, applied cross-discipline to Earth Observation.**
> CellProfiler's `TrackObjects` — built to follow **dividing nuclei** in fluorescence time-lapse microscopy — run **unchanged** through a Galaxy workflow to track **drifting icebergs** across a satellite time-series. A bright berg on a dark ocean is the EO mirror of a bright nucleus on a dark background; a **calving** berg (one object splitting into two) is the mirror of a dividing nucleus.

Part of **OSCARS-FIESTA** (cross-image analysis *with Galaxy*) — a companion to [fiesta-galaxy-bioimageio-eo](https://github.com/annefou/fiesta-galaxy-bioimageio-eo) and [fiesta-galaxy-sourceextractor-eo](https://github.com/annefou/fiesta-galaxy-sourceextractor-eo). This is **not** a replication of a paper: it reuses the Galaxy Training Network tutorial *"Object tracking using CellProfiler"* ([`gxy.io/GTN:T00516`](https://gxy.io/GTN:T00516)) and the CellProfiler software ([McQuin et al. 2018](https://doi.org/10.1371/journal.pbio.2005970)), applying the same tracking pipeline to Earth-observation data. It produces a reproducible pipeline, a Zenodo-archived release with a citable DOI, and a Science Live nanopublication chain.

## Result

The CellProfiler tracking pipeline — designed for dividing nuclei — recovers coherent iceberg tracks across a satellite time-series **run unchanged**. On a controlled, cloud-free time-series of drifting "bergs" the local same-algorithm path tracked **3 bergs across all 8 frames** and followed a **calving event** (one berg becoming two) by starting a new track for the daughter — **4 tracks total**, mean 3.12 objects/frame, max displacement 261 px. The Galaxy workflow imports onto **Galaxy Europe (usegalaxy.eu)** with **all 13 steps resolving to installed CellProfiler tools** (verified live, 2026-06-21).

![Cross-discipline object tracking](figures/main_result.png)

*(Honesty note: this demonstrates **cross-discipline method transfer**, not tracking accuracy against ground truth. The clean headline uses a controlled synthetic time-series because optical MODIS over the summer Southern Ocean is cloud-dominated, so brightness segmentation there tracks cloud/sea-ice as well as the iceberg — reliable berg-only tracking needs cloud-independent SAR. See `nanopubs/drafts/05_outcome.md`.)*

## Two ways to run — Galaxy first

This repo foregrounds the **Galaxy** path (FIESTA is about cross-image analysis *with Galaxy*):

- **Galaxy (showcased):** `notebooks/03_analysis.py` runs [`workflow/main_workflow.ga`](workflow/main_workflow.ga) — the CellProfiler module chain (Starting Modules → ColorToGray → IdentifyPrimaryObjects → MeasureObject* → TrackObjects[Overlap, 50 px] → OverlayOutlines → Tile → SaveImages → ExportToSpreadsheet) — on **usegalaxy.eu** via BioBlend. **This path needs a usegalaxy.eu API key** at `~/.galaxy_eu_key` (free account → *User → Preferences → Manage API Key*). The workflow imports and resolves all tools on usegalaxy.eu today; a first invocation also needs each CellProfiler module's default parameters completed by opening the workflow once in the usegalaxy.eu editor and saving (standard Galaxy practice — see [`workflow/`](workflow/) annotation).
- **Local fallback (CI / hermetic):** the *same algorithm* offline (scikit-image Otsu `IdentifyPrimaryObjects` + frame-to-frame overlap `TrackObjects`) — **no key needed**, so CI and the Jupyter Book build hermetically and deterministically.

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

The Jupyter Book version is at <https://annefou.github.io/fiesta-galaxy-cellprofiler-eo/>.

### Data source

`notebooks/01_data_download.py` selects its input via `FIESTA_DATA`:
`synthetic` (deterministic, cloud-free — used by CI and the headline figure), `modis` (real A-68A MODIS frames via NASA GIBS), or `auto` (default: try MODIS, fall back to synthetic). The engine is selected via `FIESTA_ENGINE`: `galaxy` or `local` (default: Galaxy if a key is present, else local).

## Repository structure

```
.
├── CLAUDE.md / AGENTS.md       # operating manual for AI assistants
├── DOMAIN.md                   # domain flavour (biodiversity + earth observation)
├── README.md                   # this file
├── LICENSE                     # MIT
├── CITATION.cff / codemeta.json / ro-crate-metadata.json
├── pixi.toml + pixi.lock       # pinned dependencies (single source of truth)
├── Dockerfile                  # container build
├── Snakefile                   # pipeline orchestration
├── myst.yml + index.md         # Jupyter Book
├── workflow/main_workflow.ga   # the Galaxy CellProfiler tracking workflow
├── notebooks/                  # jupytext .py pipeline (01–04)
├── scripts/cellprofiler_tracking.py  # Galaxy (BioBlend) + local same-algorithm driver
├── nanopubs/                   # FORRT chain drafts + published-URI registry
├── docs/                       # reference material
├── figures/                    # curated figures used in the Jupyter Book
├── .github/workflows/          # CI, Jupyter Book, Docker
└── .claude/                    # Claude Code agents, skills, sandbox config
```

## Built from a template

This repository was created from [`ScienceLiveHub/forrt-replication-template`](https://github.com/ScienceLiveHub/forrt-replication-template), part of the [Science Live platform](https://platform.sciencelive4all.org). The template bakes in FAIR4RS conformance, self-contained data downloads, `pixi` as the single source of truth, Jupyter Book deployment, Docker + GHCR + Zenodo archival, RO-Crate packaging, and a six-step FORRT chain workspace.

## FORRT nanopublication chain

The FORRT chain for this work is **drafted** field-by-field in [`nanopubs/drafts/`](nanopubs/drafts/) (question-rooted: PICO → AIDA → Claim → Study → Outcome → CiTO, plus a Research Software nanopub) and is ready to publish on [platform.sciencelive4all.org](https://platform.sciencelive4all.org). Publish each step in order and record the URIs in [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md).

## Citation

If you use this work, please cite:

- This software: [`CITATION.cff`](CITATION.cff) → concept DOI minted on first release.
- The reused software: CellProfiler — [McQuin et al. 2018](https://doi.org/10.1371/journal.pbio.2005970), [Carpenter et al. 2006](https://doi.org/10.1186/gb-2006-7-10-r100).
- The reused method: GTN tutorial *Object tracking using CellProfiler* — [`gxy.io/GTN:T00516`](https://gxy.io/GTN:T00516).
- Data: NASA MODIS via [GIBS](https://nasa-gibs.github.io/gibs-api-docs/) (iceberg A-68A).

## Acknowledgements

Built from [`ScienceLiveHub/forrt-replication-template`](https://github.com/ScienceLiveHub/forrt-replication-template). The template is licensed MIT and contributions (especially new domain flavours under [`docs/domain-flavours/`](docs/domain-flavours/)) are welcome.
