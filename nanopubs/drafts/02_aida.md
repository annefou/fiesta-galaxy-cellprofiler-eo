# 02 — AIDA Sentence

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

## Field-by-field draft

### AIDA sentence (textarea, required)

Atomic, Independent, Declarative, Absolute. One empirical finding. Ends with a full stop.

```
The CellProfiler object-tracking pipeline, built to follow dividing nuclei and applied without modification through a Galaxy workflow, recovers coherent atmospheric-river objects and their trajectories across an ERA5 IVT time-series, following an individual river for several consecutive days.
```

### Select related topics/tags (dropdown, optional)

```
object tracking; atmospheric rivers; reanalysis
```

### Relates to this nanopublication (text input, required)

URI of the PICO published in step 01.

```
<paste PICO URI from PUBLISHED.md step 01 after publishing>
```

### Supported by datasets (repeatable group, optional)

- ERA5 IVT via ARCO-ERA5 (Google Cloud public dataset): https://cloud.google.com/storage/docs/public-datasets/era5

### Supported by other publications (repeatable group, optional)

- CellProfiler 3.0 (McQuin et al. 2018): https://doi.org/10.1371/journal.pbio.2005970
- Atmospheric-river detection criteria (Guan & Waliser 2015): https://doi.org/10.1002/2015JD024257
- Galaxy Training Network tutorial *Object tracking using CellProfiler* (method): https://gxy.io/GTN:T00516

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 02.
