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
# - `figures/main_result.png` — the headline cross-discipline figure: IVT frames
#   with detected atmospheric-river outlines + centroids, plus the recovered AR
#   trajectories (centroid paths coloured by track id).
# - `figures/robustness.png` — atmospheric rivers tracked per timestep and the
#   peak IVT through the event, showing the tracker follows the rivers across the
#   whole window.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import imageio.v3 as iio
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

# %% [markdown]
# ## Headline figure — detected AR frames + recovered trajectories

# %%
n_show = min(4, n_frames)
show_idx = np.linspace(0, n_frames - 1, n_show).astype(int)
fig = plt.figure(figsize=(15, 4.4))

for col, fidx in enumerate(show_idx):
    ax = fig.add_subplot(1, n_show + 1, col + 1)
    ax.imshow(iio.imread(frames[fidx]))
    sub = df[df["frame"] == fidx]
    for _, r in sub.iterrows():
        ax.plot(r["centroid_x"], r["centroid_y"], "o", ms=6, mec="white",
                mfc=colors[r["track_id"]])
        ax.text(r["centroid_x"] + 4, r["centroid_y"], int(r["track_id"]),
                color="white", fontsize=8)
    ttl = sub["time"].iloc[0] if len(sub) else f"frame {fidx}"
    ax.set_title(ttl, fontsize=9); ax.set_xticks([]); ax.set_yticks([])

ax = fig.add_subplot(1, n_show + 1, n_show + 1)
for t in track_ids:
    g = df[df["track_id"] == t].sort_values("frame")
    ax.plot(g["centroid_x"], g["centroid_y"], "-o", ms=3, color=colors[t],
            label=f"AR {t}")
ax.invert_yaxis(); ax.set_aspect("equal")
ax.set_title("recovered AR tracks"); ax.set_xlabel("lon index"); ax.set_ylabel("lat index")
ax.legend(fontsize=7, loc="best")

fig.suptitle("Galaxy CellProfiler object-tracking applied cross-discipline to "
             "atmospheric rivers (ERA5 IVT)", fontsize=13, y=1.04)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGS / "main_result.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Robustness — ARs per timestep and peak IVT through the event

# %%
per_frame = df.groupby("frame").size().reindex(range(n_frames), fill_value=0)
peak_ivt = df.groupby("frame")["max_ivt"].max().reindex(range(n_frames))

fig, ax1 = plt.subplots(figsize=(9, 4.3))
ax1.bar(per_frame.index, per_frame.values, color="#1f77b4", alpha=0.7,
        label="ARs tracked")
ax1.set_xlabel("frame (6-hourly)"); ax1.set_ylabel("atmospheric rivers tracked",
                                                    color="#1f77b4")
ax2 = ax1.twinx()
ax2.plot(peak_ivt.index, peak_ivt.values, "-o", ms=3, color="#c1272d",
         label="peak IVT")
ax2.set_ylabel("peak IVT (kg m$^{-1}$ s$^{-1}$)", color="#c1272d")
ax1.set_title("Atmospheric rivers tracked per timestep, and peak IVT through the event")
fig.tight_layout()
fig.savefig(FIGS / "robustness.png", dpi=150, bbox_inches="tight")
plt.show()

print("wrote figures/main_result.png and figures/robustness.png")
