# The Galaxy CellProfiler run — how the workflow was assembled

**Status: green end-to-end.** `workflow/main_workflow.ga` runs the full
CellProfiler module chain on **usegalaxy.eu**, including the final monolithic
*Run CellProfiler pipeline* runner, with **all 13 steps `ok`**. Public history:
<https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad591597e3e548295>
(verified 2026-06-23, invocation `7b22ed04769eee9e`). The run produces
`TrackObjects` measurement tables + tracked PNGs. The byte-comparable local
same-algorithm path remains the CI/hermetic quantitative result.

## How the workflow was built — start from the tutorial's own `.ga`

The GTN tutorial this repo ports — *Object tracking using CellProfiler*
(`gxy.io/GTN:T00516`) — defines the canonical Galaxy method: *"A pipeline is
built by chaining together Galaxy tools representing CellProfiler modules and
must start with the Starting modules tool and end with the CellProfiler tool."*
So the workflow is the tutorial's module chain, not a single `.cppipe`.

The decisive move was to **base our `.ga` on the tutorial's own exported
workflow** rather than hand-author the per-module `tool_state`. The tutorial ships
[`main_workflow.ga`](https://raw.githubusercontent.com/galaxyproject/training-material/main/topics/imaging/tutorials/object-tracking-using-cell-profiler/workflows/main_workflow.ga)
(`CP_object_tracking_example`, 13 steps). Its module versions are identical to
ours, and — because it was exported from a real Galaxy instance — every module's
`tool_state` is already valid (it is already 2D, and every conditional field is
populated). We took that file verbatim and applied a **minimal retarget** for our
atmospheric-river data:

| Change | From → To | Why |
|---|---|---|
| Workflow name/annotation | tutorial → AR/EO description | provenance |
| Object name (steps 4–7) | `Nuclei` → `Rivers` | scientific clarity |
| TrackObjects output image | `TrackedCells` → `TrackedRivers` | scientific clarity |
| NamesAndTypes filename rule | `GFPHistone` → `frame` | match our `frame_NNN.png` |
| Metadata regex | 3-field → `(?P<field1>frame)_(?P<field2>[0-9]+)` | our naming |
| Input label | → `Image time-series (zip)` | match the BioBlend driver |

Everything else is inherited verbatim: **2D** (`process_3d: No`), **ColorToGray**
(`OrigColor` → `OrigGray`), every other module's `tool_state`, and the real
`uuid4` step ids (placeholder UUIDs would 400 on import).

### One supporting change in the data writer

The inherited NamesAndTypes declares the input a **Color image**, and the
tutorial's ColorToGray converts it to grayscale. So `notebooks/02_data_clean.py`
writes the IVT frames as **3-channel RGB** (the grayscale replicated across
R/G/B) rather than single-channel. This keeps the workflow structurally identical
to the training material's chain (ColorToGray stays) while feeding it valid
input. The local path is unaffected — it reads `data/clean/ivt.nc`, not the PNGs.

## Reproducing the run

1. Regenerate the RGB frames: `cd notebooks && python 02_data_clean.py`
   (needs `data/raw/ivt_era5.nc` from `01_data_download.py`).
2. Drive it with `scripts/cellprofiler_tracking.py` (`run_on_galaxy`), which zips
   `data/clean/frame_*.png`, uploads, imports `workflow/main_workflow.ga`, and
   invokes by input name `Image time-series (zip)`. A usegalaxy.eu API key at
   `~/.galaxy_eu_key` is required.
3. Invoke with `allow_tool_state_corrections=True` and
   `require_exact_tool_versions=False` so Galaxy resolves the tutorial's tool
   versions to whatever is installed on usegalaxy.eu.

## Appendix — why the earlier hand-authored `.ga` failed

The previous `workflow/main_workflow.ga` was hand-authored, and its per-module
`tool_state` did not survive Galaxy's tool-state correction. The assembled
pipeline had three defects, all of which the GTN-derived file avoids by
construction:

1. NamesAndTypes was set to **Process as 3D? = Yes** (frames are 2D).
2. ColorToGray was fed single-channel grayscale (mode-`L`) input.
3. IdentifyPrimaryObjects came back with **blank** input-image/object-name fields
   (the real tool uses `input_from_nat` / `name_to_be_identified` under a
   `con_advanced` conditional) and a nucleus-sized diameter.

Lesson: for CellProfiler-in-Galaxy, start from a Galaxy-exported workflow (the
tutorial's, or one extracted from a successful history) and retarget data-specific
fields — don't hand-write the deeply-nested module `tool_state`.

## After the run

- `results/galaxy_provenance.json` records the public history URL, invocation id,
  and output counts.
- `nanopubs/drafts/05_outcome.md` cites the end-to-end Galaxy run as evidence
  (the quantitative AR conclusion still rests on the local same-algorithm path).
