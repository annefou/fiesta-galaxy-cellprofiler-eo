# 01 — PICO Research Question (question-rooted)

> Chain shape: **question-rooted** (no upstream paper; this reuses a bioimaging *method* cross-discipline). See `docs/chain-decision-tree.md`.

**Form heading:** *"PICO Research Question — Define a research question using the PICO framework (Population, Intervention, Comparator, Outcome)"*

## Field-by-field draft

### Short ID (text input, required)

```
cellprofiler-trackobjects-eo-icebergs
```

### Research Question Title (text input, required)

10–200 characters.

```
Can a bioimaging object-tracking pipeline track drifting icebergs in satellite imagery via Galaxy?
```

### Complete Research Question (textarea, required)

```
In a time-series of satellite frames showing bright objects drifting on a dark ocean (Population), does the CellProfiler object-tracking pipeline — IdentifyPrimaryObjects plus TrackObjects, built to follow dividing nuclei in fluorescence time-lapse and applied without modification through a Galaxy workflow (Intervention), compared with the same algorithm run locally outside Galaxy (Comparator), recover coherent per-object trajectories across frames, including a calving event in which one object splits into two (Outcome)?
```

### Question Type (radio button, required)

- [ ] Causation
- [x] Descriptive
- [ ] Effectiveness
- [ ] Experience
- [ ] Prediction

### Population (P) (textarea, required)

```
Ordered satellite image frames of a scene containing discrete bright objects on a dark background — here a MODIS (NASA GIBS) time-series of the giant iceberg A-68A drifting past South Georgia (Dec 2020 – Jan 2021), plus a deterministic controlled stand-in time-series of drifting and calving bright "bergs" used for a cloud-free demonstration.
```

### Intervention (I) (textarea, required)

```
The CellProfiler object-tracking pipeline (Starting Modules → ColorToGray → IdentifyPrimaryObjects → MeasureObjectSizeShape → MeasureObjectIntensity → TrackObjects [Overlap method, 50 px] → OverlayOutlines → Tile → SaveImages → ExportToSpreadsheet), originally designed to segment and track dividing cell nuclei in fluorescence time-lapse microscopy, applied without modification to the satellite frames through a Galaxy workflow on usegalaxy.eu — a cross-discipline transfer of a bioimaging tracker to Earth observation.
```

### Comparison (C) (textarea, required)

```
The same IdentifyPrimaryObjects + TrackObjects algorithm (Otsu segmentation + frame-to-frame overlap tracking) run locally outside Galaxy, used to confirm the Galaxy result and to provide a hermetic, credential-free reproduction.
```

### Outcome (O) (textarea, required)

```
Recovery of coherent per-object tracks across the time-series — a persistent identity, centroid trajectory, area and intensity per object per frame — and whether the tracker follows the objects through a split (one object becoming two), the Earth-observation analogue of a dividing nucleus.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.
