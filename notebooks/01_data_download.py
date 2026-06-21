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
# Fetches a **time series of satellite frames** of the giant iceberg **A-68A**
# drifting past South Georgia (Scotia Sea) in December 2020 – January 2021, from
# **NASA GIBS** (Global Imagery Browse Services — free, anonymous, no key). Each
# date becomes one PNG frame in `data/raw/`.
#
# These drifting bergs are the Earth-observation analogue of dividing nuclei in a
# fluorescence time-lapse: many discrete bright blobs on a dark background that
# move (and split) from frame to frame. We will track them with CellProfiler's
# `TrackObjects` — the FIESTA cross-discipline experiment.
#
# **Self-contained:** the repo ships no data; this notebook is the only path that
# brings it in. **No credentials needed** for the data download. If GIBS is
# unreachable (e.g. fully offline CI), a deterministic **synthetic** time-lapse
# stand-in is generated so the pipeline always runs; `data/raw/sources.json`
# records which path was used.

# %%
import json
import os
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

RAW = Path("../data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# A-68A drift corridor N/NW of South Georgia, late 2020 (lon/lat WGS84).
BBOX = {"lon_min": -42.0, "lon_max": -34.0, "lat_min": -55.5, "lat_max": -52.5}
SIZE = 512  # output frame size (px), square
# Weekly cloud-permitting dates spanning the drift + fragmentation period.
DATES = ["2020-12-05", "2020-12-12", "2020-12-19", "2020-12-26",
         "2021-01-02", "2021-01-09", "2021-01-16", "2021-01-23"]
LAYER = "MODIS_Terra_CorrectedReflectance_Bands721"  # ice/snow contrast
GIBS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

SOURCES = [{
    "name": "MODIS Terra Corrected Reflectance (Bands 7-2-1)",
    "target": "Iceberg A-68A drift past South Georgia",
    "doi": None,
    "provider": "NASA GIBS / Worldview (LANCE/EOSDIS)",
    "url": GIBS,
    "layer": LAYER,
    "license": "public-domain (NASA EOSDIS)",
    "bbox": BBOX, "dates": DATES, "size_px": SIZE,
}]


# %% [markdown]
# ## GIBS WMS GetMap (real MODIS frames)

# %%
def gibs_url(date: str) -> str:
    # WMS 1.3.0 + EPSG:4326 uses lat,lon axis order in BBOX.
    bbox = f"{BBOX['lat_min']},{BBOX['lon_min']},{BBOX['lat_max']},{BBOX['lon_max']}"
    return (f"{GIBS}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={LAYER}"
            f"&CRS=EPSG:4326&BBOX={bbox}&WIDTH={SIZE}&HEIGHT={SIZE}"
            f"&FORMAT=image/png&TIME={date}")


def fetch_modis() -> bool:
    """Download one MODIS frame per date. Returns True if all succeeded."""
    for i, date in enumerate(DATES):
        out = RAW / f"frame_{i:03d}.png"
        if out.exists():
            print(f"  {date}: cached")
            continue
        try:
            req = urllib.request.Request(
                gibs_url(date), headers={"User-Agent": "fiesta-cellprofiler-eo"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) < 1000:                # blank/empty tile
                raise ValueError("tile too small")
            out.write_bytes(data)
            print(f"  {date}: {len(data) // 1024} KiB -> {out.name}")
        except Exception as e:  # noqa: BLE001 — any network/tile failure -> synthetic
            print(f"  {date}: FAILED ({str(e)[:60]})")
            return False
    return True


# %% [markdown]
# ## Synthetic stand-in (deterministic; used only if GIBS is unreachable)
#
# Bright Gaussian "bergs" drift left→right on a dark ocean; at the midpoint the
# largest berg **calves** into two — exercising the exact `TrackObjects` overlap
# logic (motion + a split), the EO mirror of a dividing nucleus.

# %%
def make_synthetic():
    rng = np.random.default_rng(68)            # A-68 :)
    n = len(DATES)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    # base bergs: (x0, y0, vx, vy, radius)
    bergs = [(80, 140, 34, 6, 26), (110, 300, 30, -4, 34), (60, 410, 36, 10, 20)]
    for f in range(n):
        img = rng.normal(18, 4, (SIZE, SIZE)).clip(0, 60)   # dark, noisy ocean
        active = list(bergs)
        if f >= n // 2:                         # calving: split berg #1 into two
            x0, y0, vx, vy, r = bergs[1]
            fs = f - n // 2                      # frames since the split
            active[1] = (x0, y0 - 40 - 6 * fs, vx, vy, 18)   # daughter drifts up
            active.append((x0 + 6, y0 + 40 + 6 * fs, vx + 4, vy, 16))  # other drifts down
        for (x0, y0, vx, vy, r) in active:
            cx, cy = x0 + vx * f, y0 + vy * f
            blob = 235 * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2)))
            img = np.maximum(img, blob)
        Image.fromarray(img.clip(0, 255).astype("uint8"), mode="L").save(
            RAW / f"frame_{f:03d}.png")
    print(f"  synthetic: {n} frames of drifting/calving bergs")


# %% [markdown]
# ## Choose the data source
#
# `FIESTA_DATA` selects the input:
#
# - `auto` (default): try real MODIS, fall back to synthetic if GIBS is down.
# - `modis`: require real MODIS (raise if unreachable).
# - `synthetic`: force the controlled stand-in.
#
# **CI and the committed headline figure use `synthetic`** — it is deterministic
# and cloud-free, so it cleanly demonstrates the ported `TrackObjects` capability
# (drift + a calving split) and builds hermetically. The real A-68A MODIS frames
# are downloaded with `FIESTA_DATA=modis|auto`; note that optical MODIS over the
# summer Southern Ocean is cloud-dominated, so brightness segmentation there
# tracks bright cloud/ice as well as the berg — see the README limitation.

# %%
choice = os.environ.get("FIESTA_DATA", "auto").lower()
if choice == "synthetic":
    make_synthetic()
    mode = "synthetic"
elif choice == "modis":
    if not fetch_modis():
        raise RuntimeError("FIESTA_DATA=modis but GIBS frames could not be fetched")
    mode = "modis-gibs"
else:  # auto
    mode = "modis-gibs" if fetch_modis() else "synthetic"
    if mode == "synthetic":
        print("GIBS unavailable -> generating synthetic stand-in")
        make_synthetic()

SOURCES[0]["mode"] = mode
(RAW / "sources.json").write_text(json.dumps({"sources": SOURCES}, indent=2))
print(f"\n{len(DATES)} frames in data/raw/ (mode={mode}); sources logged")
