# Finalizing the Galaxy CellProfiler run (GUI round-trip)

This is the one step that cannot be done over the API: turning the imported
workflow into a CellProfiler pipeline that the **monolithic `Run CellProfiler
pipeline` tool** executes end-to-end on **usegalaxy.eu**. Everything else (data
download, IVT computation, detection, tracking, figures, CI, Jupyter Book) is
already automated and green; the local same-algorithm path produces the
quantitative result. This guide makes the *showcased Galaxy run* green too.

## Why a GUI round-trip is needed

`workflow/main_workflow.ga` imports onto usegalaxy.eu and all 13 tools resolve;
the per-module builder steps run green and the data flows through. But the final
`Run CellProfiler pipeline` step fails, because the hand-authored per-module
`tool_state` doesn't fully survive Galaxy's tool-state correction. Verified
defects in the assembled pipeline (history checked 2026-06):

1. **NamesAndTypes → "Process as 3D? = Yes"** — our IVT frames are 2D, so the
   pipeline must be set to 2D.
2. **`ColorToGray` is in the chain, but the IVT frames are single-channel
   grayscale** (`notebooks/02_data_clean.py` writes mode-`L` PNGs). ColorToGray
   expects a colour image and errors / is meaningless here — it should be
   **removed**.
3. **IdentifyPrimaryObjects** came back with **blank** input-image and
   object-name fields (the real tool uses `input_from_nat` /
   `name_to_be_identified` under a `con_advanced` conditional, not the keys the
   hand-authored state used), and a nucleus-sized diameter (10–40 px) rather
   than something appropriate for large AR filaments.

CellProfiler modules have deeply nested conditional parameters; the Galaxy
**editor** renders each module's real form (and knows the image is grayscale),
which is why finalizing there is the standard, robust practice.

---

## Recommended: switch to a single `.cppipe` (Option A1)

Instead of the fragile 11-module builder chain, run **one** CellProfiler pipeline
file. This is the most robust Galaxy-native route.

### 1. Build the pipeline once in CellProfiler

Use **CellProfiler Desktop** (free, cellprofiler.org) — or adapt the GTN
tutorial pipeline (`gxy.io/GTN:T00516`). Build this module sequence for **2D
grayscale** frames (no ColorToGray):

| Module | Key settings for our IVT frames |
|---|---|
| Images | (default) |
| Metadata | Extract from file name; regex captures the frame index, e.g. `frame_(?P<Index>[0-9]+)` |
| NamesAndTypes | **Process as 3D? → No**; assign **all images** the grayscale name `IVT` |
| Groups | No grouping (the whole series is one movie) |
| IdentifyPrimaryObjects | Input image `IVT`; objects `Rivers`; **typical diameter ~10–400 px** (AR filaments are large); Global **Otsu, three classes**; discard border objects = No |
| MeasureObjectSizeShape | objects `Rivers` |
| MeasureObjectIntensity | image `IVT`, objects `Rivers` |
| **TrackObjects** | Method **Overlap**; object `Rivers`; **maximum distance ~50 px**; save colour-coded image `TrackedRivers` |
| OverlayOutlines | on `IVT`, outline `Rivers` |
| SaveImages | save `TrackedRivers` (and/or the outline image) as PNG |
| ExportToSpreadsheet | export per-object measurements (includes the `TrackObjects` columns: label, displacement, lifetime) |

Save as `cellprofiler_pipeline.cppipe`. Validate it runs locally on a couple of
the frames from `data/clean/` first.

> Tip: regenerate the frames any time with
> `pixi run python -c "import jupytext"` … or just
> `cd notebooks && jupytext --to notebook --execute 01_data_download.py 02_data_clean.py`
> → `data/clean/frame_*.png`.

### 2. Run it on usegalaxy.eu

1. **Upload** to a new history: (a) a **zip** of `data/clean/frame_*.png`, and
   (b) the `cellprofiler_pipeline.cppipe`.
2. Run **Unzip** on the frames zip (`imgteam/unzip`) → gives an image collection.
3. Run **Run CellProfiler pipeline** (`bgruening/cp_cellprofiler`):
   - *Pipeline file* → your `.cppipe`
   - *Are the input images packed into a tar archive?* → **No**
   - *Images* → the unzipped image collection (select the dataset collection)
4. Run. The measurements CSV + tracked PNGs appear in the history.

### 3. Capture it back into the repo

- **Extract Workflow** from the finished history (History options → *Extract
  Workflow*), then **Download** it as `.ga` and overwrite
  `workflow/main_workflow.ga`. Commit `cellprofiler_pipeline.cppipe` alongside it.
- Make the history **shareable** (History options → *Share or Publish*) and paste
  its URL into `results/galaxy_provenance.json` together with the workflow
  invocation id. The BioBlend driver (`scripts/cellprofiler_tracking.py
  → run_on_galaxy`) already uploads a frames zip and invokes the workflow, so
  with the corrected `.ga` it will run end-to-end when `~/.galaxy_eu_key` is set.

---

## Alternative: fix the existing module-chain workflow in the editor (Option A2)

If you'd rather keep the 11-module builder chain:

1. **Workflows → (the imported workflow) → Edit**.
2. **Delete the `ColorToGray` node** and connect `Starting Modules` → directly
   into `IdentifyPrimaryObjects` (the input is already grayscale).
3. Open **`Starting Modules`** → NamesAndTypes section → set **Process as 3D? =
   No**, image type **Grayscale**, name e.g. `IVT`.
4. Open **`IdentifyPrimaryObjects`** → set input image `IVT`, objects `Rivers`,
   diameter ~10–400, Global Otsu three classes.
5. Check **`TrackObjects`** (object `Rivers`, Overlap, ~50 px), **`OverlayOutlines`**,
   **`SaveImages`**, **`ExportToSpreadsheet`** all reference `Rivers` / the right
   image names.
6. Open **`Run CellProfiler pipeline`** → *tar archive?* **No**, and connect the
   **Unzip** image collection to *Images*.
7. **Save**, run once from a history to confirm green, then **Download** the `.ga`
   over `workflow/main_workflow.ga` and commit.

---

## After either option

- Update `nanopubs/drafts/05_outcome.md` to add the Galaxy invocation id + public
  history URL to the evidence (the conclusion already holds; this upgrades the
  Galaxy path from "imports + tools resolve" to "runs end-to-end").
- The local same-algorithm path remains the CI/hermetic result and cross-check.
