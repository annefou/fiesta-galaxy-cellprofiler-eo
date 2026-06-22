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
# # 04 — Figures
#
# - `figures/main_result.png` — the headline cross-discipline figure: a row of IVT
#   frames with detected atmospheric-river outlines + centroids, above a large
#   **geographic** map of the recovered AR trajectories (centroid paths in
#   longitude/latitude, coloured by track id).
# - `figures/robustness.png` — atmospheric rivers tracked per timestep and the
#   peak IVT through the event.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import imageio.v3 as iio
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import cm

CLEAN, RESULTS, FIGS = Path("../data/clean"), Path("../results"), Path("../figures")
FIGS.mkdir(parents=True, exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")

df = pd.read_csv(RESULTS / "tracks.csv")
frames = sorted(RESULTS.glob("frame_*__tracked.png"))
n_frames = len(frames)
track_ids = sorted(df["track_id"].unique())
colors = {t: cm.tab10(i % 10) for i, t in enumerate(track_ids)}

# Map centroid grid-indices -> geographic lon/lat for the trajectory map.
geo = xr.open_dataset(CLEAN / "ivt.nc")
lons = geo["longitude"].to_numpy()
lats = geo["latitude"].to_numpy()


def to_lon(cx):
    return float(lons[min(max(int(round(cx)), 0), len(lons) - 1)])


def to_lat(cy):
    return float(lats[min(max(int(round(cy)), 0), len(lats) - 1)])


df["lon"] = df["centroid_x"].map(to_lon)
df["lat"] = df["centroid_y"].map(to_lat)

# %% [markdown]
# ## Headline figure — detected AR frames (top) + recovered trajectory map (bottom)

# %%
n_show = min(4, n_frames)
# prefer frames that actually contain a detected AR, so every thumbnail is informative
det_frames = sorted(df["frame"].unique())
pool = det_frames if det_frames else list(range(n_frames))
show_idx = [pool[i] for i in np.linspace(0, len(pool) - 1, n_show).astype(int)]

fig = plt.figure(figsize=(16, 11))
gs = fig.add_gridspec(2, n_show, height_ratios=[1.0, 2.0], hspace=0.22, wspace=0.06)

# --- top row: detected AR frames ---
for col, fidx in enumerate(show_idx):
    ax = fig.add_subplot(gs[0, col])
    ax.imshow(iio.imread(frames[fidx]))
    sub = df[df["frame"] == fidx]
    for _, r in sub.iterrows():
        ax.plot(r["centroid_x"], r["centroid_y"], "o", ms=9, mec="white",
                mfc=colors[r["track_id"]], mew=1.5)
        ax.text(r["centroid_x"] + 6, r["centroid_y"], int(r["track_id"]),
                color="white", fontsize=11, weight="bold")
    ttl = sub["time"].iloc[0] if len(sub) else f"frame {fidx}"
    ax.set_title(ttl, fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])

# --- bottom: large geographic trajectory map ---
axt = fig.add_subplot(gs[1, :])
for t in track_ids:
    g = df[df["track_id"] == t].sort_values("frame")
    axt.plot(g["lon"], g["lat"], "-o", ms=5, lw=2, color=colors[t],
             label=f"AR {t} ({g['frame'].nunique()} steps, ≤{int(g['length_km'].max())} km)")
    axt.annotate(int(t), (g["lon"].iloc[0], g["lat"].iloc[0]), fontsize=11,
                 weight="bold", color=colors[t])
axt.set_xlabel("longitude (°E)", fontsize=12)
axt.set_ylabel("latitude (°N)", fontsize=12)
axt.set_title("Recovered atmospheric-river trajectories", fontsize=13)
axt.legend(fontsize=10, loc="best", framealpha=0.9)
axt.tick_params(labelsize=11)

fig.suptitle("Galaxy CellProfiler object-tracking applied cross-discipline to "
             "atmospheric rivers (ERA5 IVT, N Pacific, Feb 2017)",
             fontsize=15, y=0.95)
fig.savefig(FIGS / "main_result.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Robustness — ARs per timestep and peak IVT through the event

# %%
per_frame = df.groupby("frame").size().reindex(range(n_frames), fill_value=0)
peak_ivt = df.groupby("frame")["max_ivt"].max().reindex(range(n_frames))

fig, ax1 = plt.subplots(figsize=(11, 4.6))
ax1.bar(per_frame.index, per_frame.values, color="#1f77b4", alpha=0.7,
        label="ARs tracked")
ax1.set_xlabel("frame (6-hourly)", fontsize=12)
ax1.set_ylabel("atmospheric rivers tracked", color="#1f77b4", fontsize=12)
ax2 = ax1.twinx()
ax2.plot(peak_ivt.index, peak_ivt.values, "-o", ms=4, color="#c1272d",
         label="peak IVT")
ax2.set_ylabel("peak IVT (kg m$^{-1}$ s$^{-1}$)", color="#c1272d", fontsize=12)
ax1.set_title("Atmospheric rivers tracked per timestep, and peak IVT through the event",
              fontsize=13)
fig.tight_layout()
fig.savefig(FIGS / "robustness.png", dpi=150, bbox_inches="tight")
plt.show()

print("wrote figures/main_result.png and figures/robustness.png")
