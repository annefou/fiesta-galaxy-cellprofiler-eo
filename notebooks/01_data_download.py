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
# # 01 — Data download
#
# Downloads **ERA5 vertically-integrated water-vapour transport (IVT)** over the
# North Pacific for a window containing several **atmospheric rivers** (the very
# active early-February 2017 sequence that struck the US West Coast), from
# **ARCO-ERA5** — the analysis-ready ERA5 mirror on Google Cloud, **public and
# anonymous** (no credentials, no API key).
#
# IVT has two components — eastward and northward water-vapour flux — and its
# magnitude √(u²+v²) is the standard field used to detect atmospheric rivers
# (Guan & Waliser 2015). An AR is a long, narrow filament of high IVT; in a
# time-series it drifts, intensifies, merges and splits — the Earth-system
# analogue of the bright dividing nuclei that CellProfiler's `TrackObjects` was
# built for, which is the FIESTA cross-discipline experiment.
#
# **Self-contained & reproducible:** this notebook is the only path that brings
# in data; it pins the exact ARCO-ERA5 store, variables, region, window and
# cadence. No data is committed to the repo.

# %%
import json
import os
from pathlib import Path

import numpy as np
import xarray as xr

RAW = Path("../data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# --- ERA5 source (analysis-ready, public, anonymous) ---
STORE = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
U_VAR = "vertical_integral_of_eastward_water_vapour_flux"   # IVT eastward (kg m^-1 s^-1)
V_VAR = "vertical_integral_of_northward_water_vapour_flux"  # IVT northward (kg m^-1 s^-1)

# --- region + window (override via env for other events / CI) ---
LAT_MAX = float(os.environ.get("FIESTA_LAT_MAX", 60))
LAT_MIN = float(os.environ.get("FIESTA_LAT_MIN", 15))
LON_MIN = float(os.environ.get("FIESTA_LON_MIN", 170))   # ARCO-ERA5 longitudes are 0..360
LON_MAX = float(os.environ.get("FIESTA_LON_MAX", 250))   # 170-250E = North Pacific -> NA west coast
START = os.environ.get("FIESTA_START", "2017-02-02")
END = os.environ.get("FIESTA_END", "2017-02-11")
STRIDE_H = int(os.environ.get("FIESTA_STRIDE_H", 6))     # 6-hourly, the AR-catalog cadence

SOURCE = {
    "name": "ERA5 vertically-integrated water-vapour transport (IVT)",
    "provider": "ARCO-ERA5 (Google Cloud public dataset)", "store": STORE,
    "variables": [U_VAR, V_VAR], "license": "Copernicus / ECMWF (free, attribution)",
    "region": {"lat": [LAT_MIN, LAT_MAX], "lon": [LON_MIN, LON_MAX]},
    "window": [START, END], "cadence_hours": STRIDE_H,
    "event": "North Pacific atmospheric rivers, early February 2017",
}

# %% [markdown]
# ## Open ARCO-ERA5 and slice region + window

# %%
ds = xr.open_zarr(STORE, chunks=None, storage_options={"token": "anon"},
                  decode_timedelta=True)
sub = (ds[[U_VAR, V_VAR]]
       .sel(time=slice(START, END))
       .isel(time=slice(0, None, STRIDE_H))                 # hourly -> STRIDE_H-hourly
       .sel(latitude=slice(LAT_MAX, LAT_MIN),               # ERA5 latitude descends
            longitude=slice(LON_MIN, LON_MAX)))

# %% [markdown]
# ## Download (compute) and save as a self-describing NetCDF

# %%
sub = sub.rename({U_VAR: "ivt_u", V_VAR: "ivt_v"}).compute()
sub = sub.assign_attrs(**{f"source_{k}": json.dumps(v) if isinstance(v, (dict, list)) else v
                          for k, v in SOURCE.items()})
out = RAW / "ivt_era5.nc"
sub.to_netcdf(out)
(RAW / "sources.json").write_text(json.dumps({"sources": [SOURCE]}, indent=2))

n_t = sub.sizes["time"]
print(f"downloaded {n_t} IVT fields ({START}..{END}, every {STRIDE_H} h) -> {out.name}")
print(f"grid: {sub.sizes['latitude']} lat x {sub.sizes['longitude']} lon")
print(f"peak IVT in window: {float(np.hypot(sub.ivt_u, sub.ivt_v).max()):.0f} kg m^-1 s^-1")
