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
# # 02 — Data clean
#
# Turns the raw ERA5 IVT components into the two things the analysis needs:
#
# 1. A tidy **`data/clean/ivt.nc`** holding the eastward/northward IVT components,
#    the IVT magnitude, and the latitude axis — consumed by the detection step.
# 2. A **time-ordered series of RGB PNG frames** in `data/clean/`, where each
#    frame renders the IVT magnitude as a bright atmospheric-river filament on a
#    dark background — the exact input the Galaxy CellProfiler `TrackObjects`
#    pipeline ingests (the EO/climate mirror of bright nuclei on a dark
#    background). Frame order is the time axis the tracker links across.
#
#    The frames are written as **3-channel RGB** (the IVT grayscale replicated
#    across R/G/B) rather than single-channel, because the ported GTN pipeline
#    (`gxy.io/GTN:T00516`) keeps the tutorial's `ColorToGray` module: its
#    NamesAndTypes step declares the input a *Color image*, then converts it to
#    grayscale exactly as in the tutorial. Replicating the channel keeps our
#    workflow structurally identical to the training material's module chain.

# %%
from pathlib import Path

import numpy as np
import xarray as xr
from PIL import Image

RAW, CLEAN = Path("../data/raw"), Path("../data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)
IVT_DISPLAY_MAX = 700.0   # kg m^-1 s^-1 -> white; matches the detection dynamic range

# %%
ds = xr.open_dataset(RAW / "ivt_era5.nc")
ivt = np.hypot(ds["ivt_u"], ds["ivt_v"]).rename("ivt")
ds["ivt"] = ivt
ds.to_netcdf(CLEAN / "ivt.nc")

# %% [markdown]
# ## Render one PNG frame per timestep (bright AR on dark)

# %%
mag = ivt.to_numpy()
for f in range(mag.shape[0]):
    img = (np.clip(mag[f] / IVT_DISPLAY_MAX, 0, 1) * 255).astype("uint8")
    rgb = np.repeat(img[:, :, None], 3, axis=2)  # grayscale -> 3-channel RGB (ColorToGray input)
    Image.fromarray(rgb, mode="RGB").save(CLEAN / f"frame_{f:03d}.png")

print(f"wrote data/clean/ivt.nc + {mag.shape[0]} frames")
print(f"IVT magnitude range: {float(mag.min()):.0f} – {float(mag.max()):.0f} kg m^-1 s^-1")
