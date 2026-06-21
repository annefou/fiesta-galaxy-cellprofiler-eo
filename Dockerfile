FROM ghcr.io/prefix-dev/pixi:0.68.1

LABEL org.opencontainers.image.source="https://github.com/annefou/fiesta-galaxy-cellprofiler-eo"
LABEL org.opencontainers.image.description="Cross-discipline demo: Galaxy CellProfiler object-tracking applied to a satellite time-series of drifting icebergs (OSCARS-FIESTA)"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install the pinned environment first (separate from source copy so the lock
# layer is cached across source-only edits).
COPY pixi.toml pixi.lock /app/
RUN pixi install --locked

COPY . /app

# To run the Galaxy (usegalaxy.eu) path, mount your API key at runtime:
#   docker run -v ~/.galaxy_eu_key:/root/.galaxy_eu_key \
#       ghcr.io/annefou/fiesta-galaxy-cellprofiler-eo:latest
# Without a key the container runs the hermetic local fallback. See data/README.md.

CMD ["pixi", "run", "snakemake", "--cores", "1"]
