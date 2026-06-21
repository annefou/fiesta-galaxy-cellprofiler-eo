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
# - `figures/main_result.png` — the headline cross-discipline figure: a montage of
#   frames with tracked iceberg outlines, plus the recovered drift trajectories
#   (centroid paths coloured by track id).
# - `figures/robustness.png` — number of tracked objects per frame, showing the
#   tracker follows the bergs (and the calving/split) across the whole series.

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
frames = sorted(CLEAN.glob("frame_*.png"))
n_frames = len(frames)
track_ids = sorted(df["track_id"].unique())
colors = {t: cm.tab10(i % 10) for i, t in enumerate(track_ids)}

# %% [markdown]
# ## Headline figure — tracked frames + drift trajectories

# %%
n_show = min(4, n_frames)
show_idx = np.linspace(0, n_frames - 1, n_show).astype(int)
fig = plt.figure(figsize=(14, 4.4))

for col, fidx in enumerate(show_idx):
    ax = fig.add_subplot(1, n_show + 1, col + 1)
    tracked = RESULTS / f"{frames[fidx].stem}__tracked.png"
    base = iio.imread(tracked) if tracked.exists() else iio.imread(frames[fidx])
    ax.imshow(base)
    sub = df[df["frame"] == fidx]
    for _, r in sub.iterrows():
        ax.plot(r["centroid_x"], r["centroid_y"], "o", ms=5,
                mec="white", mfc=colors[r["track_id"]])
        ax.text(r["centroid_x"] + 6, r["centroid_y"], int(r["track_id"]),
                color="white", fontsize=8)
    ax.set_title(f"frame {fidx}"); ax.set_xticks([]); ax.set_yticks([])

# trajectory panel
ax = fig.add_subplot(1, n_show + 1, n_show + 1)
for t in track_ids:
    g = df[df["track_id"] == t].sort_values("frame")
    ax.plot(g["centroid_x"], g["centroid_y"], "-o", ms=3, color=colors[t],
            label=f"berg {t}")
ax.invert_yaxis(); ax.set_aspect("equal")
ax.set_title("recovered drift tracks"); ax.set_xlabel("x (px)"); ax.set_ylabel("y (px)")
ax.legend(fontsize=7, loc="best")

fig.suptitle("Galaxy CellProfiler object-tracking applied cross-discipline to "
             "drifting icebergs (Earth observation)", fontsize=13, y=1.04)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGS / "main_result.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Robustness — objects tracked per frame

# %%
per_frame = df.groupby("frame").size().reindex(range(n_frames), fill_value=0)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(per_frame.index, per_frame.values, color="#1f77b4")
ax.set_xlabel("frame (time)"); ax.set_ylabel("tracked objects")
ax.set_title("Objects tracked per frame across the time series\n"
             "(the tracker follows the bergs through the calving/split event)")
ax.set_xticks(range(n_frames))
fig.tight_layout()
fig.savefig(FIGS / "robustness.png", dpi=150, bbox_inches="tight")
plt.show()

print("wrote figures/main_result.png and figures/robustness.png")
