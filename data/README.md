# `data/` — downloaded artefacts, never committed

This directory holds the raw and cleaned datasets used by the pipeline. **Files here are never committed to git** (`.gitignore` excludes everything except this README).

## Why download-on-first-run

Every replication must be self-contained: a user clones the repo and runs `snakemake --cores 1` (or executes notebook 01 directly), and the code fetches its own input data — no manual steps.

## Where data comes from

`notebooks/01_data_download.py` fetches all inputs from **ARCO-ERA5** — the analysis-ready ERA5 reanalysis mirror on Google Cloud (`gs://gcp-public-data-arco-era5`), which is **public and anonymous** (`storage_options={"token": "anon"}`, no API key, no account). It downloads the two **IVT** components (vertically-integrated eastward/northward water-vapour flux) over the configured region and window and writes a self-describing `data/raw/ivt_era5.nc`. `notebooks/02_data_clean.py` computes the IVT magnitude and renders the per-timestep PNG frames the tracker ingests.

The exact store, variables, region, window and 6-hourly cadence are pinned at the top of notebook 01 and echoed into `data/raw/sources.json`, so the download is fully reproducible. Override region/window with env vars `FIESTA_LAT_MIN/MAX`, `FIESTA_LON_MIN/MAX`, `FIESTA_START`, `FIESTA_END`, `FIESTA_STRIDE_H`.

## Credentials

- **Data download:** none — ARCO-ERA5 is anonymous.
- **Galaxy analysis path (notebook 03):** the showcased run executes the CellProfiler workflow on **usegalaxy.eu (Galaxy Europe)** via BioBlend, which **requires a usegalaxy.eu API key**. Create a free account, then *User → Preferences → Manage API Key*, and save it to `~/.galaxy_eu_key`. Without it, notebook 03 uses the hermetic local fallback (same algorithm, no account). In CI the Galaxy path is skipped (`FIESTA_ENGINE=local`).

## CI cache

The default window is small (a few tens of IVT fields over one region, a few MB), so no caching is needed. For larger downloads use `actions/cache@v4` (see `.github/workflows/ci.yml`).
