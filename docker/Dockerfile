ARG SCANPY_VERSION=1.12.1
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
ARG DEBIAN_SECURITY_MIRROR=http://deb.debian.org/debian-security
ARG PIP_INDEX_URL=https://pypi.org/simple

FROM python:3.12-slim-bookworm AS builder

ARG SCANPY_VERSION
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR
ARG PIP_INDEX_URL

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=5
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PYTHONNOUSERSITE=1
ENV MPLBACKEND=Agg
ENV NUMBA_CACHE_DIR=/tmp/numba-cache
ENV XDG_CACHE_HOME=/tmp

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            build-essential \
            ca-certificates \
            gfortran \
            git \
            libopenblas-dev \
            pkg-config; then \
        break; \
      fi; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    python -m venv /opt/scanpy; \
    /opt/scanpy/bin/python -m pip install --upgrade pip setuptools wheel; \
    /opt/scanpy/bin/python -m pip install "scanpy[leiden,skmisc]==${SCANPY_VERSION}"; \
    /opt/scanpy/bin/python -m pip check; \
    /opt/scanpy/bin/python -m pip freeze --all > /opt/scanpy/requirements.freeze.txt

COPY docker/scanpy_smoke.py /opt/scanpy/share/testdata/scanpy_smoke.py

RUN set -eux; \
    chmod 0755 /opt/scanpy/share/testdata/scanpy_smoke.py; \
    mkdir -p /opt/scanpy/share/doc/scanpy; \
    mv /opt/scanpy/requirements.freeze.txt /opt/scanpy/share/doc/scanpy/requirements.freeze.txt; \
    printf "%s\n" "${SCANPY_VERSION}" > /opt/scanpy/share/doc/scanpy/VERSION

RUN set -eux; \
    export PATH="/opt/scanpy/bin:${PATH}"; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("scanpy"))')" = "${SCANPY_VERSION}"; \
    python -c 'import importlib.metadata as md; import scanpy as sc, anndata, h5py, igraph, leidenalg, matplotlib, natsort, networkx, numba, numpy, pandas, pynndescent, scipy, seaborn, sklearn, statsmodels, umap; from skmisc.loess import loess; print(md.version("scanpy"))' | grep -Fx "${SCANPY_VERSION}" >/dev/null; \
    scanpy --help 2>&1 | grep -E 'usage:|Usage:' >/dev/null; \
    tmp=/tmp/taf-scanpy-runtime-check; \
    rm -rf "$tmp"; \
    mkdir -p "$tmp"; \
    python /opt/scanpy/share/testdata/scanpy_smoke.py "$tmp/out"; \
    test -s "$tmp/out/scanpy_smoke.h5ad"; \
    test -s "$tmp/out/pca.png"; \
    test -s "$tmp/out/markers.tsv"; \
    test -s "$tmp/out/versions.tsv"; \
    rm -rf "$tmp"

FROM python:3.12-slim-bookworm

ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONNOUSERSITE=1
ENV MPLBACKEND=Agg
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV NUMBA_CACHE_DIR=/tmp/numba-cache
ENV XDG_CACHE_HOME=/tmp
ENV PATH=/opt/scanpy/bin:${PATH}
ENV SCANPY_HOME=/opt/scanpy
ENV SCANPY_TESTDATA=/opt/scanpy/share/testdata

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            bash \
            ca-certificates \
            fontconfig \
            fonts-dejavu-core \
            libgfortran5 \
            libgomp1 \
            libopenblas0-pthread \
            libstdc++6; then \
        break; \
      fi; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/scanpy /opt/scanpy

RUN set -eux; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("scanpy"))')" = "1.12.1"; \
    python -c 'import importlib.metadata as md; import scanpy as sc, anndata, h5py, igraph, leidenalg, matplotlib, natsort, networkx, numba, numpy, pandas, pynndescent, scipy, seaborn, sklearn, statsmodels, umap; from skmisc.loess import loess; print(md.version("scanpy"))' | grep -Fx "1.12.1" >/dev/null; \
    scanpy --help 2>&1 | grep -E 'usage:|Usage:' >/dev/null; \
    tmp=/tmp/taf-scanpy-runtime-check; \
    rm -rf "$tmp"; \
    mkdir -p "$tmp"; \
    python /opt/scanpy/share/testdata/scanpy_smoke.py "$tmp/out"; \
    test -s "$tmp/out/scanpy_smoke.h5ad"; \
    test -s "$tmp/out/pca.png"; \
    test -s "$tmp/out/markers.tsv"; \
    test -s "$tmp/out/versions.tsv"; \
    rm -rf "$tmp"

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=scanpy
