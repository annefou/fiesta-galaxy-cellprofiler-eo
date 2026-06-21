# `data/` — downloaded artefacts, never committed

This directory holds the raw and cleaned datasets used by the pipeline. **Files in this directory are never committed to git** (`.gitignore` excludes everything except this README).

## Why download-on-first-run

Every replication must be self-contained: a user clones the repo and runs `snakemake --cores 1` (or executes notebook 01 directly), and the code fetches its own input data. No "ask the author for the dataset" steps.

## Where data comes from

`notebooks/01_data_download.py` fetches all inputs:

- **NASA GIBS (Global Imagery Browse Services)** — a WMS `GetMap` request per date returns a MODIS Terra Corrected-Reflectance frame (no credentials) for the iceberg A-68A drift corridor near South Georgia. This is the real Earth-observation input.
- **Synthetic stand-in (deterministic, seeded)** — generated *only* if GIBS is unreachable (e.g. fully offline CI), so the pipeline always runs. `data/raw/sources.json` records which path was used (`mode: modis-gibs` or `mode: synthetic`). Set `FIESTA_REQUIRE_REAL=1` to fail instead of falling back.

For the dataset, the notebook records the exact WMS query, the layer, the bounding box, the dates, and the public-domain NASA EOSDIS license.

## Credentials

- **Data download:** none required (GIBS is anonymous).
- **Galaxy analysis path (notebook 03):** the showcased run executes the CellProfiler workflow on **usegalaxy.eu (Galaxy Europe)** via BioBlend, which **requires a usegalaxy.eu API key**. Create a free account, then *User → Preferences → Manage API Key*, and save the key to `~/.galaxy_eu_key`. Without it, notebook 03 uses the hermetic local fallback (same algorithm, no account). In CI the Galaxy path is intentionally skipped (`FIESTA_ENGINE=local`).

## CI cache

Large downloads (>100 MB) should be cached in GitHub Actions via `actions/cache@v4`. See `.github/workflows/ci.yml` for the pattern. The MODIS frames here are small (a few hundred KiB each), so caching is optional.
