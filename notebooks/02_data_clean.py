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
# Turns each raw frame into the **exact input the CellProfiler tracking pipeline
# expects**: a single-channel 8-bit grayscale PNG where the icebergs read as
# **bright objects on a dark ocean** — the remote-sensing mirror of the bright
# fluorescent nuclei the original GTN tutorial tracks.
#
# Steps (the EO analogue of the tutorial's `ColorToGray` + intensity prep):
# RGB → grayscale, percentile contrast stretch, write to `data/clean/`. The frame
# index order is preserved, because `TrackObjects` links objects *between
# consecutive frames* — order is the time axis.

# %%
from pathlib import Path

import numpy as np
import imageio.v3 as iio
from PIL import Image

RAW, CLEAN = Path("../data/raw"), Path("../data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)
SIZE = 512
P_LO, P_HI = 2, 99.5   # contrast-stretch percentiles


# %%
def clean_one(fp: Path):
    img = np.asarray(iio.imread(fp)).astype("float32")
    if img.ndim == 3:
        img = img[..., :3].mean(axis=-1)              # ColorToGray
    lo, hi = np.percentile(img, [P_LO, P_HI])
    if hi <= lo:
        hi = lo + 1.0
    stretched = np.clip((img - lo) / (hi - lo), 0, 1) * 255
    out = Image.fromarray(stretched.astype("uint8"), mode="L").resize(
        (SIZE, SIZE), Image.BILINEAR)
    out.save(CLEAN / fp.name)
    print(f"  {fp.name}: cleaned")


# %%
frames = sorted(RAW.glob("frame_*.png"))
for fp in frames:
    clean_one(fp)
print(f"clean frames ready in data/clean/ ({len(frames)} frames)")
