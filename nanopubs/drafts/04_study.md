# 04 — FORRT Replication Study

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Method verified against `notebooks/01–04` + `scripts/cellprofiler_tracking.py` + `workflow/main_workflow.ga`.

## Field-by-field draft

### Short URI suffix for study ID (text input, required)

```
cellprofiler-eo-tracking-study
```

### Label/name of replication study (text input, required)

```
Cross-discipline application of the CellProfiler tracking pipeline to satellite iceberg tracking via Galaxy
```

### Study type (dropdown, required)

- [ ] Reproduction Study — direct reproduction: same methodology, same tools.
- [x] Replication Study — replication with different methodology or conditions.
- [ ] Reproduction/Replication Study — both.

*Rationale: the CellProfiler modules, versions, and the TrackObjects Overlap method (50 px) are identical to the original microscopy tutorial; the **conditions** change (a satellite time-series of drifting icebergs instead of fluorescence time-lapse of nuclei). Same method, new data domain → Replication Study.*

### Search for a FORRT claim (search/select, required)

```
<paste Claim URI from PUBLISHED.md step 03 after publishing>
```

### Describe what part of the claim is reproduced/replicated (textarea, required)

Scope only — no method, no results.

```
Whether the tracking behaviour of the CellProfiler IdentifyPrimaryObjects + TrackObjects pipeline — assigning each bright object a persistent identity across frames, recovering its centroid trajectory, and continuing to track through a split where one object becomes two — holds when the input is a satellite image time-series of drifting icebergs rather than a fluorescence time-lapse of dividing nuclei. In scope: recovery of coherent per-object tracks (identity, trajectory, area, intensity) and the handling of a calving/split event, on (a) a controlled cloud-free synthetic time-series and (b) real MODIS frames of iceberg A-68A. Out of scope: tracking accuracy against ground-truth iceberg positions, discrimination of icebergs from cloud or sea ice in optical imagery, and any geophysical drift-velocity product.
```

### Describe how the claim is reproduced/replicated (textarea, required)

Method in plain prose — no result numbers.

```
A time-series of ordered satellite frames was prepared two ways: (a) MODIS Terra Corrected-Reflectance frames of the A-68A drift corridor near South Georgia were fetched per date from NASA GIBS via WMS GetMap; (b) a deterministic synthetic time-series of bright Gaussian "bergs" drifting on a dark ocean, with one berg calving into two at the midpoint, was generated for a cloud-free demonstration. Each frame was converted to a single-channel grayscale image with a percentile contrast stretch (bright objects on a dark background). The frames were zipped and run through the unchanged Galaxy CellProfiler workflow (main_workflow.ga) on usegalaxy.eu via BioBlend: Unzip → Starting Modules → ColorToGray → IdentifyPrimaryObjects (three-class Otsu, object diameter 30–9999 px, border objects excluded) → MeasureObjectSizeShape → MeasureObjectIntensity → TrackObjects (Overlap method, maximum displacement 50 px) → OverlayOutlines → Tile → SaveImages → ExportToSpreadsheet. The exported per-object measurements (with tracking columns) give each object's track identity, centroid, area and intensity per frame. A same-algorithm local path (scikit-image Otsu IdentifyPrimaryObjects with a 30 px minimum-diameter size filter, then frame-to-frame one-to-one maximum-overlap linking with a 50 px gate, so a split daughter starts a new track) reproduces the result without a Galaxy account for hermetic CI.
```

### Describe any deviations from original methodology (textarea, optional)

```
Relative to the original Galaxy microscopy tutorial, only the input domain changed: fluorescence time-lapse frames of dividing nuclei were replaced by satellite frames of drifting icebergs (real MODIS and a controlled synthetic stand-in). The CellProfiler module chain, versions, segmentation strategy and the TrackObjects Overlap method with a 50 px displacement gate are unchanged. No retraining or algorithm change was performed. The local fallback reimplements the same algorithm with scikit-image for a credential-free, hermetic reproduction.
```

### Search keywords (Wikidata) (multi-select, optional)

- object tracking
- image segmentation
- iceberg

### Search discipline (Wikidata) (search, optional)

- remote sensing

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
