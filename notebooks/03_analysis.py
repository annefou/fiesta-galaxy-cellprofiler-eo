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
# # 03 — Tracking analysis (Galaxy CellProfiler workflow)
#
# Runs the **CellProfiler object-tracking Galaxy workflow**
# (`workflow/main_workflow.ga`, which assembles the CellProfiler module chain and
# runs it) on the cleaned frame time-series and recovers, for every detected iceberg:
#
# - its **track id** (persistent identity across frames)
# - its **centroid** per frame (the drift trajectory)
# - its **area** and **mean intensity**
#
# **Two execution paths** (see `scripts/cellprofiler_tracking.py`):
#
# - **Galaxy (showcased):** if `~/.galaxy_eu_key` is present, the workflow runs on
#   **usegalaxy.eu** (Galaxy Europe) via BioBlend — *this is the FIESTA result:
#   cross-image analysis with Galaxy*. **A usegalaxy.eu API key is required** for
#   this path (free account → User → Preferences → Manage API Key → save it to
#   `~/.galaxy_eu_key`). The invocation id is recorded for provenance.
# - **Local fallback (CI):** otherwise the *same algorithm* runs offline
#   (skimage Otsu `IdentifyPrimaryObjects` → size filter → `TrackObjects` by
#   frame-to-frame overlap, max 50 px), so the Jupyter Book builds hermetically
#   **without a key**.

# %%
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path("../scripts").resolve()))
from cellprofiler_tracking import (segment_and_track, track_metrics,  # noqa: E402
                                   have_galaxy_key)

CLEAN, RESULTS = Path("../data/clean"), Path("../results")
RESULTS.mkdir(parents=True, exist_ok=True)
print("execution path:", "Galaxy (usegalaxy.eu)" if have_galaxy_key()
      else "local skimage fallback")

# %% [markdown]
# ## Run the tracking workflow on the frame series

# %%
out = segment_and_track(CLEAN, RESULTS)
print("engine:", out["engine"],
      "| invocation:", out.get("invocation_id", "(local)"))

# The local path returns the tracks DataFrame directly; the Galaxy path returns a
# downloaded measurements CSV — load whichever we got into one tidy table.
if "tracks_df" in out:
    df = out["tracks_df"]
else:
    df = pd.read_csv(out["track"])
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
# fluorescence time-lapse — follows **drifting icebergs** across a satellite
# time-series **unchanged**: it assigns each berg a persistent identity, recovers
# its frame-to-frame trajectory, and keeps tracking through a **calving/split**
# event (one object becoming two). The Galaxy run and the local same-algorithm
# fallback recover the same tracks. This is the cross-discipline transfer claim:
# a bioimaging tracker applied to Earth observation, run through Galaxy.
