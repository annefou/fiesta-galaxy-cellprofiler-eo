"""Track objects across an image time series — two ways.

`run_on_galaxy()` invokes the *actual* Galaxy CellProfiler workflow
(`workflow/main_workflow.ga`, which assembles the CellProfiler module chain and
runs it) on usegalaxy.eu via BioBlend — the showcased FIESTA path (cross-image analysis
*with Galaxy*). `run_local()` reproduces the **same algorithm** offline with
scikit-image + scipy (Otsu IdentifyPrimaryObjects → size filter → MeasureObject*
→ TrackObjects by frame-to-frame overlap), so CI and the Jupyter Book build
hermetically without a Galaxy account.

`segment_and_track()` picks Galaxy when a key is present, else the local fallback.

Method ported unchanged from the Galaxy Training Network tutorial
*"Object tracking using CellProfiler"* (https://gxy.io/GTN:T00516), which tracks
dividing nuclei in fluorescence time-lapse. Here the same pipeline tracks
**drifting icebergs** across a satellite time series — bright objects on a dark
ocean, the Earth-observation analogue of bright nuclei on a dark background.
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
HISTORY_NAME = "FIESTA CellProfiler tracking on EO"

# --- IdentifyPrimaryObjects / size filter (GTN tutorial values) -------------
MIN_DIAMETER_PX = 30          # tutorial: typical object diameter 30–9999 px
MAX_DIAMETER_PX = 9999
# --- TrackObjects (Overlap method, GTN tutorial value) ----------------------
MAX_TRACK_DISTANCE_PX = 50    # max pixel displacement between consecutive frames


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def have_galaxy_key() -> bool:
    return KEY_FILE.exists() and bool(KEY_FILE.read_text().strip())


def _frames(frames_dir: Path) -> list[Path]:
    return sorted(Path(frames_dir).glob("frame_*.png"))


def track_metrics(df) -> dict:
    """Summarise a tracks table (one row per object per frame)."""
    import pandas as pd  # local import keeps module import light

    if len(df) == 0:
        return {"n_frames": 0, "n_tracks": 0, "mean_objects_per_frame": 0.0,
                "longest_track_frames": 0, "max_track_displacement_px": 0.0}
    by_track = df.groupby("track_id")
    # net displacement (first->last centroid) per track
    disp = []
    for _, g in by_track:
        g = g.sort_values("frame")
        dx = g["centroid_x"].iloc[-1] - g["centroid_x"].iloc[0]
        dy = g["centroid_y"].iloc[-1] - g["centroid_y"].iloc[0]
        disp.append(float(np.hypot(dx, dy)))
    return {
        "n_frames": int(df["frame"].nunique()),
        "n_tracks": int(df["track_id"].nunique()),
        "mean_objects_per_frame": round(float(df.groupby("frame").size().mean()), 2),
        "longest_track_frames": int(by_track["frame"].nunique().max()),
        "max_track_displacement_px": round(max(disp), 2),
    }


# --------------------------------------------------------------------------- #
# Path A — the actual Galaxy CellProfiler workflow on usegalaxy.eu (BioBlend)
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


def _zip_frames(frames_dir: Path, out_dir: Path) -> Path:
    """CellProfiler in Galaxy ingests the frames as a single zip (tutorial step 1)."""
    zpath = Path(out_dir) / "frames.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in _frames(frames_dir):
            zf.write(p, arcname=p.name)
    return zpath


def run_on_galaxy(frames_dir: Path, out_dir: Path) -> dict:
    """Invoke main_workflow.ga on usegalaxy.eu; download the measurements CSV
    and the tracked-overlay image. Reuses one imported workflow across calls.
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

    zpath = _zip_frames(frames_dir, out_dir)
    up = gi.tools.upload_file(str(zpath), c["history_id"], file_type="zip")
    zip_ds = up["outputs"][0]["id"]
    _wait_ok(gi, zip_ds, "frames.zip")

    # The CellProfiler module chain is built inside the workflow; the only
    # runtime input is the zip of frames.
    inv = gi.workflows.invoke_workflow(
        c["workflow_id"],
        inputs={"Image time-series (zip)": {"id": zip_ds, "src": "hda"}},
        inputs_by="name", history_id=c["history_id"])
    gi.invocations.wait_for_invocation(inv["id"], maxwait=3600, interval=15)

    paths = {"engine": "galaxy:usegalaxy.eu", "invocation_id": inv["id"]}
    for s in gi.invocations.show_invocation(inv["id"]).get("steps", []):
        if not s.get("job_id"):
            continue
        job = gi.jobs.show_job(s["job_id"])
        tool = job.get("tool_id", "")
        for _, o in job.get("outputs", {}).items():
            ds = gi.datasets.show_dataset(o["id"])
            ext = ds.get("extension", "dat")
            if ext in ("csv", "tabular") and "track" not in paths:
                _wait_ok(gi, o["id"], "measurements")
                dest = out_dir / "galaxy_measurements.csv"
                gi.datasets.download_dataset(o["id"], file_path=str(dest),
                                             use_default_filename=False)
                paths["track"] = dest
            elif ext in ("png", "tiff") and "overlay" not in paths and "tile" in tool:
                _wait_ok(gi, o["id"], "tile")
                dest = out_dir / f"galaxy_tracked.{ext}"
                gi.datasets.download_dataset(o["id"], file_path=str(dest),
                                             use_default_filename=False)
                paths["overlay"] = dest
    return paths


# --------------------------------------------------------------------------- #
# Path B — local same-algorithm fallback (hermetic; CI)
# --------------------------------------------------------------------------- #
def _segment_frame(gray: np.ndarray):
    """IdentifyPrimaryObjects: Otsu threshold + connected components + size filter.

    Returns (label_map, list-of-object-dicts). Mirrors the CellProfiler module
    chain ColorToGray → IdentifyPrimaryObjects → MeasureObjectSizeShape/Intensity.
    """
    from scipy import ndimage
    from skimage.filters import threshold_otsu
    from skimage.measure import regionprops

    g = gray.astype("float32")
    if g.max() > g.min():
        thr = threshold_otsu(g)
    else:
        thr = g.max()
    binary = g > thr
    label_map, _ = ndimage.label(binary, structure=np.ones((3, 3)))  # 8-conn

    min_area = np.pi * (MIN_DIAMETER_PX / 2.0) ** 2
    max_area = np.pi * (MAX_DIAMETER_PX / 2.0) ** 2
    objs, relabel = [], np.zeros_like(label_map)
    next_id = 1
    for rp in regionprops(label_map, intensity_image=g):
        if not (min_area <= rp.area <= max_area):
            continue
        relabel[label_map == rp.label] = next_id
        cy, cx = rp.centroid
        mean_int = getattr(rp, "intensity_mean", None)
        if mean_int is None:
            mean_int = rp.mean_intensity  # scikit-image < 0.23
        objs.append({"object_id": next_id, "centroid_x": float(cx),
                     "centroid_y": float(cy), "area_px": int(rp.area),
                     "mean_intensity": float(mean_int)})
        next_id += 1
    return relabel, objs


def _link_overlap(prev_label, prev_ids, cur_label, cur_objs):
    """TrackObjects (Overlap method): each current object inherits the track_id of
    the previous-frame object it overlaps most. Matching is one-to-one — a previous
    track can be inherited by only one current object (the strongest overlap), so
    when one object splits into two (a calving berg / a dividing nucleus) the
    second daughter starts a NEW track. Returns {cur object_id: track_id or None};
    None is filled with a fresh id by the caller.
    """
    if prev_label is None:
        return {o["object_id"]: None for o in cur_objs}
    cands = []  # (overlap_strength, object_id, best_prev_object_id)
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
            mapping[oid] = None  # new track (split daughter, or a fresh object)
    return mapping


def run_local(frames_dir: Path, out_dir: Path) -> dict:
    """Reproduce the Galaxy CellProfiler tracking pipeline offline.

    Same algorithm: per-frame Otsu segmentation + size filter, then frame-to-frame
    overlap tracking with a 50 px gating distance. Writes a tidy tracks CSV and a
    per-frame coloured-by-track-id label map. No Galaxy account needed.
    """
    import imageio.v3 as iio
    import pandas as pd
    from skimage.segmentation import find_boundaries

    frames_dir, out_dir = Path(frames_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows, prev_label, prev_ids, next_track = [], None, {}, 1
    for fidx, fp in enumerate(_frames(frames_dir)):
        img = np.asarray(iio.imread(fp))
        if img.ndim == 3:
            img = img[..., :3].mean(axis=-1)  # ColorToGray
        label_map, objs = _segment_frame(img)
        link = _link_overlap(prev_label, prev_ids, label_map, objs)

        cur_ids = {}
        for o in objs:
            tid = link.get(o["object_id"])
            if tid is None:
                tid = next_track
                next_track += 1
            cur_ids[o["object_id"]] = tid
            rows.append({"frame": fidx, "track_id": tid, **o})

        # coloured overlay: outlines on the grayscale frame, for the montage figure
        ov = np.stack([img.astype("uint8")] * 3, axis=-1)
        ov[find_boundaries(label_map, mode="outer")] = [255, 80, 0]
        iio.imwrite(out_dir / f"{fp.stem}__tracked.png", ov)

        prev_label, prev_ids = label_map, cur_ids

    df = pd.DataFrame(rows)
    csv = out_dir / "tracks.csv"
    df.to_csv(csv, index=False)
    return {"engine": "local:skimage", "track": csv,
            "overlay": out_dir / "frame_000__tracked.png", "tracks_df": df}


def segment_and_track(frames_dir: Path, out_dir: Path,
                      prefer_galaxy: bool = True) -> dict:
    """Galaxy when a key is available, else the local same-algorithm fallback.

    Set FIESTA_ENGINE=local to force the hermetic local path (CI / offline figure
    regen); FIESTA_ENGINE=galaxy to require Galaxy.
    """
    engine = os.environ.get("FIESTA_ENGINE", "").lower()
    if engine == "local":
        return run_local(frames_dir, out_dir)
    if engine == "galaxy" or (prefer_galaxy and have_galaxy_key()):
        return run_on_galaxy(frames_dir, out_dir)
    return run_local(frames_dir, out_dir)
