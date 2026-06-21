# Snakefile — orchestrates the cross-discipline pipeline end-to-end.
#
# Each rule wraps a jupytext notebook (the notebook stays the source of truth).
# notebooks/03 runs the CellProfiler tracking workflow on usegalaxy.eu when a key
# is present (~/.galaxy_eu_key), else the same-algorithm local fallback.
#
# Usage:
#   snakemake --cores 1            # run everything
#   snakemake --cores 1 -n         # dry run

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


rule all:
    input:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/robustness.png",
        f"{RESULTS}/tracks.csv",


# ---------- 01: Data download (NASA GIBS MODIS; synthetic fallback; self-contained) ----------
rule data_download:
    output:
        f"{DATA}/raw/sources.json",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 01_data_download.py 2>&1 | tee ../{{log}}"


# ---------- 02: Data clean (-> grayscale bright-berg frames) ----------
rule data_clean:
    input:
        f"{DATA}/raw/sources.json",
    output:
        f"{DATA}/clean/frame_000.png",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 02_data_clean.py"


# ---------- 03: Tracking (Galaxy CellProfiler workflow or local fallback) ----------
rule analysis:
    input:
        f"{DATA}/clean/frame_000.png",
    output:
        f"{RESULTS}/tracks.csv",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 03_analysis.py"


# ---------- 04: Figures ----------
rule figures:
    input:
        f"{RESULTS}/tracks.csv",
    output:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/robustness.png",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 04_figures.py"
