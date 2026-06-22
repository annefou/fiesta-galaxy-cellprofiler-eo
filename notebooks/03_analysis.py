# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 03 — Detection & tracking (Galaxy CellProfiler workflow)
#
# Detects and tracks **atmospheric rivers** across the ERA5 IVT time-series,
# applying the established criteria of Guan & Waliser (2015) / tARget v4 /
# ARTMIP (Shields et al. 2018): threshold IVT at **250 kg m⁻¹ s⁻¹**, keep
# elongated objects (**length > 2000 km**, **length/width > 2**) with a
# **poleward moisture flux > 50 kg m⁻¹ s⁻¹**, then link them across consecutive
# 6-hourly steps by **overlap** (the `TrackObjects` "Overlap" method).
#
# **Two execution paths** (see `scripts/cellprofiler_tracking.py`):
#
# - **Galaxy (showcased):** if `~/.galaxy_eu_key` is present, the IVT frames are
#   run through the CellProfiler object-tracking workflow (`workflow/main_workflow.ga`)
#   on **usegalaxy.eu** (Galaxy Europe) via BioBlend — *the FIESTA result:
#   cross-image analysis with Galaxy*. **A usegalaxy.eu API key is required** for
#   this path (free account → Preferences → Manage API Key → `~/.galaxy_eu_key`).
# - **Local (default / CI):** the *same algorithm* runs offline with scikit-image
#   + scipy and the full Guan-Waliser criteria — hermetic, **no key needed**.

# %%
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path("../scripts").resolve()))
from cellprofiler_tracking import (track_ivt_series, track_metrics,  # noqa: E402
                                   have_galaxy_key)

CLEAN, RESULTS = Path("../data/clean"), Path("../results")
RESULTS.mkdir(parents=True, exist_ok=True)
print("Galaxy key present:", have_galaxy_key(),
      "(local same-algorithm path is the default and produces the tracks below)")

# %% [markdown]
# ## Detect + track ARs across the IVT series

# %%
ds = xr.open_dataset(CLEAN / "ivt.nc")
lats = ds["latitude"].to_numpy()
times = ds["time"].to_numpy()
out = track_ivt_series(ds["ivt_u"].to_numpy(), ds["ivt_v"].to_numpy(),
                       lats, times, RESULTS)
df = out["tracks_df"]
df.to_csv(RESULTS / "tracks.csv", index=False)

# %% [markdown]
# ## Track-level summary

# %%
summary = track_metrics(df)
summary["engine"] = out["engine"]
(RESULTS / "track_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
df.head(12)

# %% [markdown]
# ## What this shows
#
# CellProfiler's `TrackObjects` — designed to follow dividing nuclei in
# fluorescence time-lapse — tracks **atmospheric rivers** across an ERA5 IVT
# time-series **unchanged**: it gives each river a persistent identity, recovers
# its centroid trajectory, and follows it as it intensifies, drifts and (where it
# happens) splits. This is the cross-discipline transfer claim: a bioimaging
# object tracker applied to Earth-system science. The local path runs the full
# Guan-Waliser AR criteria; the Galaxy path runs the same segmentation + overlap
# tracking through the CellProfiler tools on usegalaxy.eu.
