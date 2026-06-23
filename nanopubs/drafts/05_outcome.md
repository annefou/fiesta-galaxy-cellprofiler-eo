# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Numbers verified against `results/track_summary.json` + `results/tracks.csv`; Galaxy status verified live against usegalaxy.eu.

## Field-by-field draft

### Short URI suffix for outcome ID (text input, required)

```
cellprofiler-ar-tracking-outcome
```

### Plain-text label for the outcome (text input, required)

```
CellProfiler tracker recovers coherent atmospheric-river tracks cross-discipline
```

### Search for a FORRT replication study (search/select, required)

```
<paste Study URI from PUBLISHED.md step 04 after publishing>
```

### Repository URL (text input, required)

```
https://github.com/annefou/fiesta-galaxy-cellprofiler-eo
```

### Completion date (date picker, required)

```
2026-06-22
```

### Validation status (dropdown, required)

- [x] Validated
- [ ] PartiallySupported
- [ ] Contradicted

*Validated for the descriptive/feasibility claim: the bioimaging tracking pipeline transfers cross-discipline and recovers coherent atmospheric-river objects and trajectories. This is NOT a detection-accuracy validation against a reference AR catalog — see limitations.*

### Confidence level (dropdown, required)

```
Moderate
```

*One basin and one multi-day event; the recovered tracks are coherent and physically reasonable, but not benchmarked against an independent AR catalog.*

### Describe the overall conclusion about the original claim (textarea, required)

```
The CellProfiler object-tracking pipeline (IdentifyPrimaryObjects + TrackObjects, Overlap method), built to follow dividing nuclei in fluorescence time-lapse and applied without modification, detects and tracks atmospheric rivers across an ERA5 IVT time-series. On the early-February 2017 North Pacific atmospheric-river sequence (6-hourly), it recovered five distinct AR tracks across the ten-day window and followed one persistent river for twenty-two consecutive 6-hourly steps (about five and a half days). The same Galaxy CellProfiler workflow runs end-to-end on Galaxy Europe (usegalaxy.eu) with all thirteen steps green — including the final Run CellProfiler pipeline runner — producing TrackObjects tracking measurements on a public history, demonstrating the cross-discipline method transfer executes in the Galaxy environment. The bioimaging "track many bright objects, including ones that divide" behaviour therefore carries over to Earth-system object tracking.
```

### Describe the evidence that supports your conclusion (textarea, required)

```
ERA5 IVT, North Pacific (15-60N, 170-250E), 2017-02-02 to 2017-02-11, 6-hourly, ARCO-ERA5 (anonymous). Detection used the Guan & Waliser (2015) criteria (IVT > 250, length > 2000 km, length/width > 2, poleward flux > 50). Local same-algorithm path (results/track_summary.json): 5 AR tracks; mean 1.33 ARs per detected frame; longest track = 22 frames (about 5.5 days); maximum AR length = 9,559 km; peak IVT in window = 1,625 kg m^-1 s^-1. Per-object tracks (frame, time, track_id, centroid, length_km, IVT, poleward) are in results/tracks.csv; the headline montage + recovered trajectories are in figures/main_result.png and the ARs-per-timestep + peak-IVT plot in figures/robustness.png. Galaxy Europe verification (live, 2026-06-23): workflow/main_workflow.ga — rebuilt from the GTN tutorial's own workflow (gxy.io/GTN:T00516) and retargeted to the IVT frames — runs end-to-end with all 13 steps green, including the final Run CellProfiler pipeline runner; the run produced TrackObjects tracking tables (93 object-instances across the series, 11 TrackObjects columns incl. displacement, distance-travelled, lifetime, trajectory) and tracked PNGs on a public history (https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad591597e3e548295). The Galaxy run uses the tutorial's default CellProfiler parameters; the quantitative AR characterisation above (Guan & Waliser criteria) is the byte-comparable local same-algorithm path.
```

### Describe what limits the conclusions of the study (textarea, optional)

```
This establishes feasibility of cross-discipline method transfer, not detection accuracy: the recovered ARs are not benchmarked against an independent reference catalog (e.g. tARget/ARTMIP), so agreement with community AR databases is not quantified here. A single basin and a single multi-day event were analysed, with one fixed IVT threshold (250 kg m^-1 s^-1) rather than the percentile-based threshold used in some catalogs. The Galaxy run executes end-to-end but uses the tutorial's default CellProfiler parameters (object size and threshold inherited from gxy.io/GTN:T00516), so its tracked objects are not filtered by the AR-specific geometric and physical criteria; the quantitative AR tracks reported here are from the byte-comparable local same-algorithm path, which applies the full Guan & Waliser criteria.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
