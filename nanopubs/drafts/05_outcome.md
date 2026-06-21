# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Numbers verified against `results/track_summary.json` + `results/tracks.csv`; Galaxy status verified live against usegalaxy.eu (see note).

## Field-by-field draft

### Short URI suffix for outcome ID (text input, required)

```
cellprofiler-eo-tracking-outcome
```

### Plain-text label for the outcome (text input, required)

```
CellProfiler tracker recovers coherent iceberg tracks (incl. a calving split) cross-discipline
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
2026-06-21
```

### Validation status (dropdown, required)

- [x] Validated
- [ ] PartiallySupported
- [ ] Contradicted

*Validated for the descriptive/feasibility claim: the bioimaging tracking pipeline transfers cross-discipline and recovers coherent object tracks including a split. This is NOT a tracking-accuracy validation against ground-truth iceberg positions — see limitations.*

### Confidence level (dropdown, required)

```
Moderate
```

*The controlled cloud-free demonstration is unambiguous; on real optical MODIS the same workflow runs but cannot, by brightness alone, separate icebergs from cloud/sea ice.*

### Describe the overall conclusion about the original claim (textarea, required)

```
The CellProfiler object-tracking pipeline (IdentifyPrimaryObjects + TrackObjects, Overlap method, 50 px), built to follow dividing nuclei in fluorescence time-lapse and applied without modification, recovers coherent per-object trajectories of drifting bright objects across a satellite image time-series. On a controlled cloud-free time-series of drifting "bergs" it tracked three objects across all eight frames and followed a calving event — one object becoming two — by starting a new track for the daughter, giving four tracks total. The same Galaxy CellProfiler workflow imports onto Galaxy Europe (usegalaxy.eu) with all thirteen steps resolving to installed tools, demonstrating the cross-discipline method transfer runs in the Galaxy environment. The bioimaging "track many bright blobs, including ones that divide" behaviour therefore carries over to Earth-observation object tracking.
```

### Describe the evidence that supports your conclusion (textarea, required)

```
Controlled synthetic time-series (8 frames), local same-algorithm path (results/track_summary.json): n_tracks = 4, mean objects per frame = 3.12, longest track = 8 frames (full series), maximum track displacement = 261.5 px; the calving at the midpoint is recovered as a new track. Per-object tracks (frame, track_id, centroid, area, intensity) are in results/tracks.csv; the headline montage + recovered drift trajectories are in figures/main_result.png and the objects-per-frame plot in figures/robustness.png. Galaxy Europe verification (live, 2026-06-21): the BioBlend driver authenticates to usegalaxy.eu; workflow/main_workflow.ga imports successfully with all 13 steps resolving to installed CellProfiler tool versions. Real MODIS frames of iceberg A-68A near South Georgia (NASA GIBS) download and run through the same local pipeline.
```

### Describe what limits the conclusions of the study (textarea, optional)

```
This establishes feasibility of cross-discipline method transfer, not tracking accuracy: there is no comparison against ground-truth iceberg positions, so recovered trajectories are not validated as correct drift tracks. On real optical MODIS imagery the Southern Ocean is heavily cloud-covered in summer, so brightness-based segmentation detects cloud and sea ice as well as the iceberg; reliable iceberg-only identification would require cloud masking or cloud-independent SAR (e.g. Sentinel-1) — hence the clean headline result uses a controlled synthetic time-series. The Galaxy run was verified to import and resolve all tools, but a full invocation additionally requires completing each CellProfiler module's default parameters by opening the workflow once in the usegalaxy.eu editor (standard Galaxy practice); the quantitative tracks reported here are from the byte-comparable local same-algorithm path. A single scene/berg, one tracking method (Overlap), optical imagery only.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
