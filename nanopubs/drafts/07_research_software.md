# 07 — Research Software (optional layer)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Scope note:** the reusable artefact here is the **parameterised Galaxy CellProfiler tracking workflow plus its BioBlend driver** (`workflow/main_workflow.ga` + `scripts/cellprofiler_tracking.py`) — others can `git clone` it and point the same tracking workflow at their own image time-series / region. That is a reusable cross-image-analysis tool, not a one-off paper reproduction, so a Research Software nanopub is appropriate. (The upstream CellProfiler software and the GTN tutorial are credited separately at the CiTO step.)

**Form heading:** *"Research Software — Describe research software with metadata including repository, supporting publications, and related resources."*

## Field-by-field draft

### URI of published software (text input, required)

Zenodo concept DOI URL (minted at the v0.1.0 release).

```
https://doi.org/10.5281/zenodo.PENDING-FIRST-RELEASE
```

### Software Title (text input, required)

```
FIESTA — Galaxy CellProfiler object-tracking workflow for cross-discipline Earth-observation tracking
```

### Repository URL (text input, required)

```
https://github.com/annefou/fiesta-galaxy-cellprofiler-eo
```

### Research Project (text input, optional)

Back-link to the FORRT Claim at the head of the chain.

```
<paste Claim URI from PUBLISHED.md step 03 after publishing>
```

### License (text input, optional)

```
https://spdx.org/licenses/MIT.html
```

### Related Datasets (repeatable group, optional)

- https://nasa-gibs.github.io/gibs-api-docs/ (MODIS via NASA GIBS)

### Related Publications (repeatable group, optional)

- `<paste Outcome URI from PUBLISHED.md step 05 after publishing>` (the FORRT Outcome this software implements)
- https://gxy.io/GTN:T00516 (reused Galaxy training/method)
- https://doi.org/10.1371/journal.pbio.2005970 (reused CellProfiler software)

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 07.
