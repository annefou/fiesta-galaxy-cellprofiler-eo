# 03 — FORRT Claim

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

## Field-by-field draft

### Short URI suffix as claim ID (text input, required)

```
cellprofiler-eo-tracking-transfer
```

### Label of the claim (text input, required)

```
CellProfiler nucleus-tracking pipeline tracks drifting icebergs via Galaxy
```

### Search for an AIDA sentence (search/select, required)

URI of the AIDA published in step 02.

```
<paste AIDA URI from PUBLISHED.md step 02 after publishing>
```

### Type of FORRT claim (dropdown, required)

See `docs/claim-type-vocabulary.md`.

- [ ] computational performance
- [ ] scalability
- [ ] data quality
- [ ] data governance
- [x] descriptive pattern
- [ ] model performance
- [ ] statistical significance

*Rationale: the claim describes a recovered pattern (coherent object trajectories, including a split) when a bioimaging tracker is applied cross-discipline. We do not benchmark tracking accuracy against ground-truth iceberg positions, so this is a `descriptive pattern` (feasibility / transfer) claim, not a `model performance` (accuracy) claim — see the Outcome limitations.*

### Source URI (text input, optional)

```
https://github.com/annefou/fiesta-galaxy-cellprofiler-eo
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 03.
