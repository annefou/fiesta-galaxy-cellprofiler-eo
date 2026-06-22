# 01 — PICO Research Question (question-rooted)

> Chain shape: **question-rooted** (no upstream paper; this reuses a bioimaging *method* cross-discipline). See `docs/chain-decision-tree.md`.

**Form heading:** *"PICO Research Question — Define a research question using the PICO framework (Population, Intervention, Comparator, Outcome)"*

## Field-by-field draft

### Short ID (text input, required)

```
cellprofiler-trackobjects-atmospheric-rivers
```

### Research Question Title (text input, required)

10–200 characters.

```
Can a bioimaging object-tracking pipeline detect and track atmospheric rivers in ERA5 IVT via Galaxy?
```

### Complete Research Question (textarea, required)

```
In a time-series of ERA5 integrated water-vapour transport (IVT) fields containing atmospheric rivers (Population), does the CellProfiler object-tracking pipeline — IdentifyPrimaryObjects plus TrackObjects, built to follow dividing nuclei in fluorescence time-lapse and applied without modification through a Galaxy workflow (Intervention), compared with the same algorithm run locally outside Galaxy (Comparator), recover coherent atmospheric-river objects and their trajectories across consecutive 6-hourly time steps, including rivers that intensify, drift and split (Outcome)?
```

### Question Type (radio button, required)

- [ ] Causation
- [x] Descriptive
- [ ] Effectiveness
- [ ] Experience
- [ ] Prediction

### Population (P) (textarea, required)

```
Gridded fields of integrated water-vapour transport (IVT) from the ERA5 reanalysis (here the North Pacific, early February 2017, 6-hourly, 0.25 degrees), in which atmospheric rivers appear as long narrow filaments of high IVT.
```

### Intervention (I) (textarea, required)

```
The CellProfiler object-tracking pipeline (IdentifyPrimaryObjects + MeasureObjectSizeShape + TrackObjects), originally designed to segment and track dividing cell nuclei in fluorescence time-lapse microscopy, applied without modification to the IVT fields through a Galaxy workflow on usegalaxy.eu — a cross-discipline transfer of a bioimaging tracker to Earth-system science. Atmospheric rivers are identified using the established Guan & Waliser (2015) criteria (IVT threshold, length, length/width ratio, poleward flux).
```

### Comparison (C) (textarea, required)

```
The same detection + overlap-tracking algorithm run locally outside Galaxy (scikit-image + scipy), used to confirm the Galaxy result and to provide a hermetic, credential-free reproduction.
```

### Outcome (O) (textarea, required)

```
Recovery of coherent atmospheric-river objects per timestep — each with a persistent identity, centroid trajectory, length, IVT intensity and poleward flux — and whether the tracker follows them across time as they intensify, drift, merge and split.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.
