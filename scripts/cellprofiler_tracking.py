"""Detect and track atmospheric rivers across an ERA5 IVT time series — two ways.

`run_on_galaxy()` invokes the *actual* Galaxy CellProfiler workflow
(`workflow/main_workflow.ga`, which assembles the CellProfiler module chain and
runs it) on usegalaxy.eu via BioBlend — the showcased FIESTA path (cross-image
analysis *with Galaxy*): the IVT fields are fed as image frames and CellProfiler
segments + tracks the bright river objects.

`track_ivt_series()` reproduces the **same idea** offline with scikit-image +
scipy, applying the established atmospheric-river detection criteria of
Guan & Waliser (2015, doi:10.1002/2015JD024257) / tARget v4 / ARTMIP
(Shields et al. 2018, doi:10.5194/gmd-11-2455-2018): threshold IVT, keep
elongated objects (length > 2000 km, length/width > 2) with a poleward moisture
flux, then link them frame-to-frame by overlap (the TrackObjects "Overlap"
method). This runs hermetically for CI and the Jupyter Book without a Galaxy key.

The cross-discipline FIESTA experiment: CellProfiler's object tracker — built to
follow dividing nuclei in fluorescence time-lapse — applied unchanged to track
atmospheric rivers (bright elongated IVT filaments that drift, merge and split)
across a reanalysis time series.
"""
from __future__ import annotations

import json
import os
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_GA = ROOT / "workflow" / "main_workflow.ga"

GALAXY_URL = "https://usegalaxy.eu"
KEY_FILE = Path.home() / ".galaxy_eu_key"
CACHE = ROOT / "results" / ".galaxy_cache.json"
HISTORY_NAME = "FIESTA CellProfiler AR tracking on ERA5 IVT"

# --- Atmospheric-river detection criteria (Guan & Waliser 2015; tARget v4) ---
IVT_THRESHOLD = 250.0     # kg m^-1 s^-1 — fixed IVT threshold (Rutz-style)
MIN_LENGTH_KM = 2000.0    # AR length must exceed 2000 km
MIN_LW_RATIO = 2.0        # length/width ratio must exceed 2
MIN_POLEWARD_IVT = 50.0   # minimum poleward IVT component (kg m^-1 s^-1)
GRID_KM = 27.75           # ~ km per 0.25 deg at the equator (lon scaled by cos(lat))


def have_galaxy_key() -> bool:
    return KEY_FILE.exists() and bool(KEY_FILE.read_text().strip())


# --------------------------------------------------------------------------- #
# Detection + tracking (local, full literature criteria)
# --------------------------------------------------------------------------- #
def detect_ars(ivt_u: np.ndarray, ivt_v: np.ndarray, lats: np.ndarray) -> tuple:
    """One timestep: threshold IVT, label objects, keep ARs that satisfy the
    Guan & Waliser geometry + poleward criteria.

    Returns (ivt_magnitude, label_map_of_kept_ARs, list-of-object-dicts).
    `lats` is the per-row latitude (length = n rows), used for km scaling and to
    define the poleward (towards-the-pole) direction in each hemisphere.
    """
    from scipy import ndimage
    from skimage.measure import regionprops

    ivt = np.hypot(ivt_u, ivt_v)
    label_map, _ = ndimage.label(ivt > IVT_THRESHOLD, structure=np.ones((3, 3)))

    kept = np.zeros_like(label_map)
    objs, nid = [], 1
    for rp in regionprops(label_map):
        ys, xs = rp.coords[:, 0], rp.coords[:, 1]
        row_lat = float(lats[ys].mean())
        # mean km/pixel for this object's latitude band (lon spacing shrinks poleward)
        km_per_px = np.hypot(GRID_KM, GRID_KM * np.cos(np.deg2rad(row_lat))) / np.sqrt(2)
        length_km = rp.axis_major_length * km_per_px
        ratio = rp.axis_major_length / max(rp.axis_minor_length, 1.0)
        # poleward IVT = towards the pole: +northward in N hemisphere, -northward in S
        mean_v = float(ivt_v[ys, xs].mean())
        poleward = mean_v if row_lat >= 0 else -mean_v
        if length_km > MIN_LENGTH_KM and ratio > MIN_LW_RATIO and poleward > MIN_POLEWARD_IVT:
            kept[label_map == rp.label] = nid
            cy, cx = rp.centroid
            objs.append({
                "object_id": nid, "centroid_x": float(cx), "centroid_y": float(cy),
                "area_px": int(rp.area), "length_km": round(length_km),
                "lw_ratio": round(float(ratio), 1),
                "mean_ivt": round(float(ivt[ys, xs].mean())),
                "max_ivt": round(float(ivt[ys, xs].max())),
                "poleward_ivt": round(poleward)})
            nid += 1
    return ivt, kept, objs


def _link_overlap(prev_label, prev_ids, cur_label, cur_objs):
    """TrackObjects (Overlap): each AR inherits the track_id of the previous-step
    AR it overlaps most; matching is one-to-one, so a split AR starts a new track.
    Returns {object_id: track_id or None}.
    """
    if prev_label is None:
        return {o["object_id"]: None for o in cur_objs}
    cands = []
    for o in cur_objs:
        overlap = prev_label[cur_label == o["object_id"]]
        overlap = overlap[overlap > 0]
        if overlap.size:
            counts = np.bincount(overlap)
            cands.append((int(counts.max()), o["object_id"], int(counts.argmax())))
        else:
            cands.append((0, o["object_id"], None))
    mapping, used = {}, set()
    for strength, oid, best_prev in sorted(cands, key=lambda c: -c[0]):
        if best_prev is not None and strength > 0 and best_prev not in used:
            mapping[oid] = prev_ids.get(best_prev)
            used.add(best_prev)
        else:
            mapping[oid] = None
    return mapping


def track_ivt_series(ivt_u, ivt_v, lats, times, out_dir: Path) -> dict:
    """Detect + track ARs across a stack of IVT fields (time, y, x).

    Writes a tidy tracks CSV and per-frame outline overlays; returns the result
    dict with the tracks DataFrame. Same algorithm CellProfiler runs in Galaxy.
    """
    import imageio.v3 as iio
    import pandas as pd
    from skimage.segmentation import find_boundaries

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, prev_label, prev_ids, next_track = [], None, {}, 1

    for f in range(ivt_u.shape[0]):
        ivt, label_map, objs = detect_ars(ivt_u[f], ivt_v[f], lats)
        link = _link_overlap(prev_label, prev_ids, label_map, objs)
        cur = {}
        for o in objs:
            tid = link.get(o["object_id"])
            if tid is None:
                tid = next_track
                next_track += 1
            cur[o["object_id"]] = tid
            rows.append({"frame": f, "time": str(times[f])[:13], "track_id": tid, **o})

        disp = np.clip(ivt / 700.0, 0, 1)
        ov = (np.stack([disp] * 3, axis=-1) * 255).astype("uint8")
        ov[find_boundaries(label_map, mode="outer")] = [0, 255, 255]
        iio.imwrite(out_dir / f"frame_{f:03d}__tracked.png", ov)

        prev_label, prev_ids = label_map, cur

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "tracks.csv", index=False)
    return {"engine": "local:skimage", "track": out_dir / "tracks.csv", "tracks_df": df}


def track_metrics(df) -> dict:
    """Summarise an AR tracks table (one row per AR per timestep)."""
    if len(df) == 0:
        return {"n_frames": 0, "n_ar_tracks": 0, "mean_ars_per_frame": 0.0,
                "longest_track_frames": 0, "max_length_km": 0, "max_ivt": 0}
    return {
        "n_frames": int(df["frame"].nunique()),
        "n_ar_tracks": int(df["track_id"].nunique()),
        "mean_ars_per_frame": round(float(df.groupby("frame").size().mean()), 2),
        "longest_track_frames": int(df.groupby("track_id")["frame"].nunique().max()),
        "max_length_km": int(df["length_km"].max()),
        "max_ivt": int(df["max_ivt"].max()),
    }


# --------------------------------------------------------------------------- #
# Galaxy path — the actual CellProfiler workflow on usegalaxy.eu (BioBlend)
# --------------------------------------------------------------------------- #
def _cache() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _save_cache(c: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c, indent=2))


def _wait_ok(gi, ds_id, what):
    while True:
        st = gi.datasets.show_dataset(ds_id)["state"]
        if st == "ok":
            return
        if st in ("error", "failed_metadata", "discarded"):
            raise RuntimeError(f"{what} failed: {st}")
        time.sleep(5)


def run_on_galaxy(frames_dir: Path, out_dir: Path) -> dict:
    """Invoke main_workflow.ga on usegalaxy.eu over the IVT frames; download the
    CellProfiler measurements CSV. Requires a usegalaxy.eu API key at
    ~/.galaxy_eu_key. The CellProfiler module chain segments + tracks the bright
    IVT river objects across the frame series.
    """
    from bioblend.galaxy import GalaxyInstance

    frames_dir, out_dir = Path(frames_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    gi = GalaxyInstance(GALAXY_URL, key=KEY_FILE.read_text().strip())
    c = _cache()
    if not c.get("history_id"):
        c["history_id"] = gi.histories.create_history(HISTORY_NAME)["id"]
        _save_cache(c)
    if not c.get("workflow_id"):
        c["workflow_id"] = gi.workflows.import_workflow_from_local_path(
            str(WORKFLOW_GA))["id"]
        _save_cache(c)

    zpath = out_dir / "frames.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(frames_dir.glob("frame_*.png")):
            zf.write(p, arcname=p.name)
    up = gi.tools.upload_file(str(zpath), c["history_id"], file_type="zip")
    zid = up["outputs"][0]["id"]
    _wait_ok(gi, zid, "frames.zip")

    inv = gi.workflows.invoke_workflow(
        c["workflow_id"], inputs={"Image time-series (zip)": {"id": zid, "src": "hda"}},
        inputs_by="name", history_id=c["history_id"])
    gi.invocations.wait_for_invocation(inv["id"], maxwait=3600, interval=15)

    paths = {"engine": "galaxy:usegalaxy.eu", "invocation_id": inv["id"]}
    for s in gi.invocations.show_invocation(inv["id"]).get("steps", []):
        if not s.get("job_id"):
            continue
        job = gi.jobs.show_job(s["job_id"])
        for _, o in job.get("outputs", {}).items():
            if gi.datasets.show_dataset(o["id"]).get("extension") in ("csv", "tabular") \
                    and "track" not in paths:
                _wait_ok(gi, o["id"], "measurements")
                dest = out_dir / "galaxy_measurements.csv"
                gi.datasets.download_dataset(o["id"], file_path=str(dest),
                                             use_default_filename=False)
                paths["track"] = dest
    return paths
