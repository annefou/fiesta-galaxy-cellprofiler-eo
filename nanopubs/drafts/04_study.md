# 04 — FORRT Replication Study

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Method verified against `notebooks/01–04` + `scripts/cellprofiler_tracking.py` + `workflow/main_workflow.ga`.

## Field-by-field draft

### Short URI suffix for study ID (text input, required)

```
cellprofiler-ar-tracking-study
```

### Label/name of replication study (text input, required)

```
Cross-discipline application of the CellProfiler tracking pipeline to atmospheric-river tracking via Galaxy
```

### Study type (dropdown, required)

- [ ] Reproduction Study — direct reproduction: same methodology, same tools.
- [x] Replication Study — replication with different methodology or conditions.
- [ ] Reproduction/Replication Study — both.

*Rationale: the CellProfiler modules and the TrackObjects Overlap method are identical to the original microscopy tutorial; the **conditions** change (an ERA5 IVT reanalysis time-series of atmospheric rivers instead of a fluorescence time-lapse of nuclei). Same method, new data domain → Replication Study.*

### Search for a FORRT claim (search/select, required)

```
<paste Claim URI from PUBLISHED.md step 03 after publishing>
```

### Describe what part of the claim is reproduced/replicated (textarea, required)

Scope only — no method, no results.

```
Whether the object-tracking behaviour of the CellProfiler IdentifyPrimaryObjects + TrackObjects pipeline — assigning each object a persistent identity across frames and recovering its trajectory, including objects that intensify, merge and split — holds when the input is a time-series of ERA5 IVT fields containing atmospheric rivers rather than a fluorescence time-lapse of dividing nuclei. In scope: recovery of coherent atmospheric-river objects (identity, trajectory, length, IVT intensity, poleward flux) and their tracking over consecutive 6-hourly steps for a North Pacific event. Out of scope: detection accuracy against a reference AR catalog (e.g. tARget/ARTMIP), landfall impacts, and precipitation attribution.
```

### Describe how the claim is reproduced/replicated (textarea, required)

Method in plain prose — no result numbers.

```
ERA5 vertically-integrated water-vapour transport (IVT) components were downloaded from ARCO-ERA5 (the analysis-ready ERA5 mirror on Google Cloud, anonymous) over the North Pacific for an early-February 2017 window at 6-hourly cadence, and the IVT magnitude was computed as the root-sum-square of the eastward and northward components. Each timestep was rendered as a single-channel frame (bright river on dark background). The frames were run through the unchanged Galaxy CellProfiler object-tracking workflow (main_workflow.ga) on usegalaxy.eu via BioBlend: IdentifyPrimaryObjects, MeasureObjectSizeShape, MeasureObjectIntensity, then TrackObjects with the Overlap method to link objects across consecutive frames. Atmospheric rivers were identified with the established Guan & Waliser (2015) / ARTMIP criteria: IVT above 250 kg m^-1 s^-1, object length above 2000 km, length/width ratio above 2, and a poleward IVT component above 50 kg m^-1 s^-1. A same-algorithm local path (scikit-image connected-component detection with the identical geometry and poleward criteria, then one-to-one maximum-overlap linking) reproduces the result without a Galaxy account for hermetic CI.
```

### Describe any deviations from original methodology (textarea, optional)

```
Relative to the original Galaxy microscopy tutorial, only the input domain changed: fluorescence time-lapse frames of dividing nuclei were replaced by ERA5 IVT fields of atmospheric rivers. The CellProfiler module chain and the TrackObjects Overlap method are unchanged. Domain-appropriate object criteria (the Guan & Waliser AR thresholds: IVT, length, length/width ratio, poleward flux) replace the nucleus size/intensity thresholds, since "what counts as an object" is necessarily domain-specific. No retraining or algorithm change was performed.
```

### Search keywords (Wikidata) (multi-select, optional)

- atmospheric river
- object tracking
- water vapor transport

### Search discipline (Wikidata) (search, optional)

- atmospheric science

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
