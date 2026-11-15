ARG PYTHON_IMAGE=python:3.13-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
# Source identity is pinned, but Debian repositories and transitive PyPI dependencies
# remain live: package availability and resolved dependencies can drift. Retain the
# image dependency receipt; retry transport failures without changing checksums.
# This is not a permanent byte-identical rebuild guarantee or an upstream mirror.
ARG SCANPY_VERSION=1.13.0
ARG SCANPY_UPSTREAM_COMMIT=3962176e93ba148bc0f61443c517877d736f2b3b
ARG SCANPY_WHEEL_URL=https://files.pythonhosted.org/packages/27/61/4312a11e9036d8bfe392db95cb77399bbd659207934d1a95352b0158fb99/scanpy-1.13.0-py3-none-any.whl
ARG SCANPY_WHEEL_SHA256=1a93f9d2136f1441ae5dfd3fcdbc3d809f6f15cc6581ab7863cd17c5c4cdd22d
ARG SKMISC_VERSION=0.5.2
ARG SKMISC_SDIST_URL=https://files.pythonhosted.org/packages/02/71/d6d2d1710fb56473817b0520212d33874069952dcb417614f6dd24efb51e/scikit_misc-0.5.2.tar.gz
ARG SKMISC_SDIST_SHA256=49fa30e4051b341edc7422db66a12c0f59d468729285bfe644d10924dc51be0a
ARG OPENPYXL_VERSION=3.1.5
ARG OPENPYXL_WHEEL_URL=https://files.pythonhosted.org/packages/c0/da/977ded879c29cbd04de313843e76868e6e13408a94ed6b987245dc7c8506/openpyxl-3.1.5-py2.py3-none-any.whl
ARG OPENPYXL_WHEEL_SHA256=5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2
ARG ET_XMLFILE_VERSION=2.0.0
ARG ET_XMLFILE_WHEEL_URL=https://files.pythonhosted.org/packages/c1/8b/5fe2cc11fee489817272089c4203e679c63b570a5aaeb18d852ae3cbba6a/et_xmlfile-2.0.0-py3-none-any.whl
ARG ET_XMLFILE_WHEEL_SHA256=7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa
ARG SCANPY_DATASET_CATALOG_SHA256=0ed3e3a3e7b04363ecaeb9943efdbc631ec2dd7f2585d249dd6a08824ae29887
ARG SCANPY_HELPER_SHA256=7ad57b8767724aa9a4042e34775e6c4fad9904ca8aa37e5ed52137c2f3df6420
ARG SCANPY_POLICY_SHA256=3599d39c7065b5a906540a62753b71b6a82e58c0b0dbaed4a6f39cb34406e28f
ARG SCANPY_SMOKE_SHA256=9c62900e8d3285bccb2cf30a5c1783598423d48c8f07af1a08d178cd947629e7
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
ARG DEBIAN_SECURITY_MIRROR=http://deb.debian.org/debian-security
ARG PIP_INDEX_URL=https://pypi.org/simple

FROM ${PYTHON_IMAGE} AS requirements

ARG PYTHON_IMAGE
ARG SCANPY_VERSION
ARG SCANPY_UPSTREAM_COMMIT
ARG SCANPY_WHEEL_URL
ARG SCANPY_WHEEL_SHA256
ARG SKMISC_VERSION
ARG SKMISC_SDIST_URL
ARG SKMISC_SDIST_SHA256
ARG OPENPYXL_VERSION
ARG OPENPYXL_WHEEL_URL
ARG OPENPYXL_WHEEL_SHA256
ARG ET_XMLFILE_VERSION
ARG ET_XMLFILE_WHEEL_URL
ARG ET_XMLFILE_WHEEL_SHA256
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
ENV XDG_CACHE_HOME=/tmp/xdg-cache

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
    export PATH="/opt/scanpy/bin:${PATH}"; \
    /opt/scanpy/bin/python -m pip install --only-binary=:all: \
      "pip==26.2.1" \
      "setuptools==84.0.0" \
      "wheel==0.48.0" \
      "packaging==26.3" \
      "meson-python==0.20.0" \
      "meson==1.12.0" \
      "Cython==3.3.0" \
      "ninja==1.13.0" \
      "patchelf==0.19.1.0" \
      "pyproject-metadata==0.12.1"; \
    # formulaic's prerelease lower bound otherwise admits a newer development build.
    /opt/scanpy/bin/python -m pip install --only-binary=:all: \
      "wrapt==2.5.2" "scanpy[leiden] @ ${SCANPY_WHEEL_URL}#sha256=${SCANPY_WHEEL_SHA256}"; \
    /opt/scanpy/bin/python -m pip install --only-binary=:all: --no-deps \
      "et-xmlfile @ ${ET_XMLFILE_WHEEL_URL}#sha256=${ET_XMLFILE_WHEEL_SHA256}" \
      "openpyxl @ ${OPENPYXL_WHEEL_URL}#sha256=${OPENPYXL_WHEEL_SHA256}"; \
    /opt/scanpy/bin/python -c \
      'import sys, urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' \
      "${SKMISC_SDIST_URL}" "/tmp/scikit_misc-${SKMISC_VERSION}.tar.gz"; \
    printf '%s  %s\n' \
      "${SKMISC_SDIST_SHA256}" "/tmp/scikit_misc-${SKMISC_VERSION}.tar.gz" \
      | sha256sum -c -; \
    /opt/scanpy/bin/python -c \
      'import importlib.metadata as md; from packaging.version import Version; assert Version(md.version("numpy")) >= Version("2.0")'; \
    /opt/scanpy/bin/python -m pip install --no-build-isolation --no-deps \
      "/tmp/scikit_misc-${SKMISC_VERSION}.tar.gz"; \
    /opt/scanpy/bin/python -m pip install --only-binary=:all: \
      "wrapt==2.5.2" "scanpy[leiden,scanpy2] @ ${SCANPY_WHEEL_URL}#sha256=${SCANPY_WHEEL_SHA256}"; \
    /opt/scanpy/bin/python -m pip uninstall --yes \
      Cython meson meson-python ninja patchelf pyproject-metadata setuptools wheel; \
    /opt/scanpy/bin/python -m pip check; \
    actual="$(/opt/scanpy/bin/python -c 'import importlib.metadata as md; print(md.version("scikit-misc"))')"; test "$actual" = "${SKMISC_VERSION}"; \
    actual="$(/opt/scanpy/bin/python -c 'import importlib.metadata as md; print(md.version("openpyxl"))')"; test "$actual" = "${OPENPYXL_VERSION}"; \
    actual="$(/opt/scanpy/bin/python -c 'import importlib.metadata as md; print(md.version("et-xmlfile"))')"; test "$actual" = "${ET_XMLFILE_VERSION}"; \
    /opt/scanpy/bin/python -m pip freeze --all > /opt/scanpy/requirements.freeze.txt

FROM requirements AS builder

ARG SCANPY_DATASET_CATALOG_SHA256
ARG SCANPY_HELPER_SHA256
ARG SCANPY_POLICY_SHA256
ARG SCANPY_SMOKE_SHA256

RUN mkdir -p /opt/scanpy/share/testdata /opt/scanpy/share/scanpy \
    && chmod 0755 /opt /opt/scanpy /opt/scanpy/share /opt/scanpy/share/testdata /opt/scanpy/share/scanpy
COPY --chmod=0755 docker/scanpy_smoke.py /opt/scanpy/share/testdata/scanpy_smoke.py
COPY --chmod=0755 docker/scanpy-prepare-datasets /opt/scanpy/bin/scanpy-prepare-datasets
COPY --chmod=0644 docker/scanpy-resource-catalog.json /opt/scanpy/share/scanpy/dataset-catalog.json
COPY --chmod=0644 docker/scanpy-sitecustomize.py /opt/scanpy/lib/python3.13/site-packages/sitecustomize.py

RUN set -eux; \
    printf '%s  %s\n' \
      "${SCANPY_HELPER_SHA256}" /opt/scanpy/bin/scanpy-prepare-datasets \
      "${SCANPY_POLICY_SHA256}" /opt/scanpy/lib/python3.13/site-packages/sitecustomize.py \
      "${SCANPY_SMOKE_SHA256}" /opt/scanpy/share/testdata/scanpy_smoke.py \
      "${SCANPY_DATASET_CATALOG_SHA256}" /opt/scanpy/share/scanpy/dataset-catalog.json \
      | sha256sum -c -; \
    chmod 0755 \
      /opt/scanpy/share/testdata/scanpy_smoke.py \
      /opt/scanpy/bin/scanpy-prepare-datasets; \
    chmod 0644 /opt/scanpy/lib/python3.13/site-packages/sitecustomize.py; \
    mkdir -p /opt/scanpy/share/doc/scanpy; \
    printf '%s\n' \
      'TAFFISH disables implicit Scanpy dataset downloads unless a persistent root is explicitly selected.' \
      > /opt/scanpy/share/scanpy/TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED; \
    chmod 0444 /opt/scanpy/share/scanpy/TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED; \
    mv /opt/scanpy/requirements.freeze.txt /opt/scanpy/share/doc/scanpy/requirements.freeze.txt; \
    cp "/opt/scanpy/lib/python3.13/site-packages/scanpy-${SCANPY_VERSION}.dist-info/licenses/LICENSE" \
      /opt/scanpy/share/doc/scanpy/LICENSE.upstream; \
    cp "/opt/scanpy/lib/python3.13/site-packages/scikit_misc-${SKMISC_VERSION}.dist-info/LICENSE" \
      /opt/scanpy/share/doc/scanpy/LICENSE.scikit-misc; \
    cp "/opt/scanpy/lib/python3.13/site-packages/openpyxl-${OPENPYXL_VERSION}.dist-info/LICENCE.rst" \
      /opt/scanpy/share/doc/scanpy/LICENSE.openpyxl; \
    cp "/opt/scanpy/lib/python3.13/site-packages/et_xmlfile-${ET_XMLFILE_VERSION}.dist-info/LICENCE.rst" \
      /opt/scanpy/share/doc/scanpy/LICENSE.et-xmlfile; \
    cp "/opt/scanpy/lib/python3.13/site-packages/et_xmlfile-${ET_XMLFILE_VERSION}.dist-info/LICENCE.python" \
      /opt/scanpy/share/doc/scanpy/LICENSE.et-xmlfile-python; \
    tar -xOf "/tmp/scikit_misc-${SKMISC_VERSION}.tar.gz" \
      "scikit_misc-${SKMISC_VERSION}/skmisc/loess/LICENSE.txt" \
      > /opt/scanpy/share/doc/scanpy/LICENSE.scikit-misc-loess; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.scikit-misc-loess; \
    rm -f "/tmp/scikit_misc-${SKMISC_VERSION}.tar.gz"; \
    printf "%s\n" "${SCANPY_VERSION}" > /opt/scanpy/share/doc/scanpy/VERSION; \
    printf '%s\n' \
      'upstream_repo=https://github.com/scverse/scanpy' \
      "upstream_tag=${SCANPY_VERSION}" \
      "upstream_commit=${SCANPY_UPSTREAM_COMMIT}" \
      "scanpy_version=${SCANPY_VERSION}" \
      "wheel_url=${SCANPY_WHEEL_URL}" \
      "wheel_sha256=${SCANPY_WHEEL_SHA256}" \
      "scikit_misc_version=${SKMISC_VERSION}" \
      "scikit_misc_sdist_url=${SKMISC_SDIST_URL}" \
      "scikit_misc_sdist_sha256=${SKMISC_SDIST_SHA256}" \
      "openpyxl_version=${OPENPYXL_VERSION}" \
      "openpyxl_wheel_url=${OPENPYXL_WHEEL_URL}" \
      "openpyxl_wheel_sha256=${OPENPYXL_WHEEL_SHA256}" \
      "et_xmlfile_version=${ET_XMLFILE_VERSION}" \
      "et_xmlfile_wheel_url=${ET_XMLFILE_WHEEL_URL}" \
      "et_xmlfile_wheel_sha256=${ET_XMLFILE_WHEEL_SHA256}" \
      "dataset_catalog_sha256=${SCANPY_DATASET_CATALOG_SHA256}" \
      "dataset_helper_sha256=${SCANPY_HELPER_SHA256}" \
      "dataset_policy_sha256=${SCANPY_POLICY_SHA256}" \
      "smoke_script_sha256=${SCANPY_SMOKE_SHA256}" \
      'scikit_misc_build_toolchain=pip==26.2.1,setuptools==84.0.0,wheel==0.48.0,packaging==26.3,meson-python==0.20.0,meson==1.12.0,Cython==3.3.0,ninja==1.13.0,patchelf==0.19.1.0,pyproject-metadata==0.12.1' \
      "base_image=${PYTHON_IMAGE}" \
      'python_requirement=>=3.13' \
      'scope=Scanpy CPU core plus leiden, scikit-misc, ScanpyV2Preview and openpyxl-backed reading' \
      'gui=default Matplotlib and optional standalone HoloViews/Bokeh HTML; no hosted service' \
      'resources=selected fixed example datasets use an explicit verified personal/site helper; implicit downloads fail closed by default' \
      'dataset_policy=managed-v1 with persistent verified or explicit unverified roots' \
      > /opt/scanpy/share/doc/scanpy/SOURCE

# Build-time checks are small, non-rendering, offline probes on both native runners.
# Full graphs, JIT-heavy neighbors, ranked-gene figures and resources run after build.
RUN set -eux; \
    export PATH="/opt/scanpy/bin:${PATH}"; \
    actual="$(python -c 'import importlib.metadata as md; print(md.version("scanpy"))')"; test "$actual" = "${SCANPY_VERSION}"; \
    python -c 'import importlib.metadata as md; import scanpy as sc, anndata, et_xmlfile, fast_array_utils, h5py, igraph, leidenalg, matplotlib, natsort, networkx, numba, numpy, openpyxl, pandas, pynndescent, scipy, scverse_misc, seaborn, sklearn, statsmodels, umap; from skmisc.loess import loess; print(md.version("scanpy"))' | grep -Fx "${SCANPY_VERSION}" >/dev/null; \
    scanpy --help 2>&1 | grep -E 'usage:|Usage:' >/dev/null; \
    grep -Fx "scanpy_version=${SCANPY_VERSION}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "wheel_sha256=${SCANPY_WHEEL_SHA256}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "scikit_misc_sdist_sha256=${SKMISC_SDIST_SHA256}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "openpyxl_wheel_sha256=${OPENPYXL_WHEEL_SHA256}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "et_xmlfile_wheel_sha256=${ET_XMLFILE_WHEEL_SHA256}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    printf '%s  %s\n' "${SCANPY_DATASET_CATALOG_SHA256}" \
      /opt/scanpy/share/scanpy/dataset-catalog.json | sha256sum -c -; \
    printf '%s  %s\n' \
      "${SCANPY_HELPER_SHA256}" /opt/scanpy/bin/scanpy-prepare-datasets \
      "${SCANPY_POLICY_SHA256}" /opt/scanpy/lib/python3.13/site-packages/sitecustomize.py \
      "${SCANPY_SMOKE_SHA256}" /opt/scanpy/share/testdata/scanpy_smoke.py \
      | sha256sum -c -; \
    scanpy-prepare-datasets --list-datasets | grep -F 'pbmc3k-raw' >/dev/null; \
    scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run | grep -F 'pbmc3k-raw' >/dev/null; \
    find /opt/scanpy/lib/python3.13/site-packages -type d \
      \( -name test -o -name tests \) -prune -exec rm -rf '{}' +; \
    rm -rf /opt/scanpy/lib/python3.13/site-packages/numpy/_core/include; \
    find /opt/scanpy/lib/python3.13/site-packages -type f \
      \( -name '*.a' -o -name '*.so.debug' \) -delete; \
    find /opt/scanpy -type d -name __pycache__ -prune -exec rm -rf '{}' +; \
    find /opt/scanpy -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete; \
    rm -rf /tmp/numba-cache /tmp/xdg-cache /root/.cache

FROM ${PYTHON_IMAGE}

ARG SCANPY_VERSION
ARG SKMISC_VERSION
ARG SKMISC_SDIST_SHA256
ARG OPENPYXL_VERSION
ARG OPENPYXL_WHEEL_SHA256
ARG ET_XMLFILE_VERSION
ARG ET_XMLFILE_WHEEL_SHA256
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONNOUSERSITE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MPLBACKEND=Agg
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV NUMBA_CACHE_DIR=/tmp/numba-cache
ENV XDG_CACHE_HOME=/tmp/xdg-cache
ENV PATH=/opt/scanpy/bin:${PATH}
ENV SCANPY_HOME=/opt/scanpy
ENV SCANPY_TESTDATA=/opt/scanpy/share/testdata
ENV TAFFISH_SCANPY_DATASET_POLICY=managed-v1
ENV TAFFISH_SCANPY_DATASETDIR=/opt/scanpy/share/scanpy/TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    runtime_tbb=""; \
    if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
      runtime_tbb="libtbb12"; \
    fi; \
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
            libstdc++6 \
            $runtime_tbb; then \
        break; \
      fi; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

ARG SCANPY_DATASET_CATALOG_SHA256
ARG SCANPY_HELPER_SHA256
ARG SCANPY_POLICY_SHA256
ARG SCANPY_SMOKE_SHA256

COPY --from=builder /opt/scanpy /opt/scanpy

RUN set -eux; \
    python -m pip check; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("scanpy"))')" = "${SCANPY_VERSION}"; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("scikit-misc"))')" = "${SKMISC_VERSION}"; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("openpyxl"))')" = "${OPENPYXL_VERSION}"; \
    test "$(python -c 'import importlib.metadata as md; print(md.version("et-xmlfile"))')" = "${ET_XMLFILE_VERSION}"; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.upstream; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.scikit-misc; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.scikit-misc-loess; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.openpyxl; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.et-xmlfile; \
    test -s /opt/scanpy/share/doc/scanpy/LICENSE.et-xmlfile-python; \
    grep -Fx "scikit_misc_sdist_sha256=${SKMISC_SDIST_SHA256}" \
      /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    if grep -Ei '^(Cython|meson|meson-python|ninja|patchelf|pyproject-metadata|setuptools|wheel)==' \
      /opt/scanpy/share/doc/scanpy/requirements.freeze.txt; then exit 1; fi; \
    grep -Fx "openpyxl_wheel_sha256=${OPENPYXL_WHEEL_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "et_xmlfile_wheel_sha256=${ET_XMLFILE_WHEEL_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "dataset_catalog_sha256=${SCANPY_DATASET_CATALOG_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    printf '%s  %s\n' "${SCANPY_DATASET_CATALOG_SHA256}" /opt/scanpy/share/scanpy/dataset-catalog.json | sha256sum -c -; \
    grep -Fx "dataset_helper_sha256=${SCANPY_HELPER_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "dataset_policy_sha256=${SCANPY_POLICY_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    grep -Fx "smoke_script_sha256=${SCANPY_SMOKE_SHA256}" /opt/scanpy/share/doc/scanpy/SOURCE >/dev/null; \
    printf '%s  %s\n' \
      "${SCANPY_HELPER_SHA256}" /opt/scanpy/bin/scanpy-prepare-datasets \
      "${SCANPY_POLICY_SHA256}" /opt/scanpy/lib/python3.13/site-packages/sitecustomize.py \
      "${SCANPY_SMOKE_SHA256}" /opt/scanpy/share/testdata/scanpy_smoke.py \
      | sha256sum -c -; \
    python -c 'import importlib.metadata as md; import scanpy as sc, anndata, et_xmlfile, fast_array_utils, h5py, igraph, leidenalg, matplotlib, natsort, networkx, numba, numpy, openpyxl, pandas, pynndescent, scipy, scverse_misc, seaborn, sklearn, statsmodels, umap; from skmisc.loess import loess; print(md.version("scanpy"))' | grep -Fx "${SCANPY_VERSION}" >/dev/null; \
    scanpy-prepare-datasets --list-datasets | grep -F 'pbmc3k-raw' >/dev/null; \
    scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run | grep -F 'pbmc3k-raw' >/dev/null; \
    scanpy --help >/dev/null; \
    python -c 'import scanpy as sc; from pathlib import Path; assert sc.settings.datasetdir.is_file(); assert sc.settings.preset is sc.Preset.ScanpyV1; import holoviews, bokeh, hv_anndata, illico'; \
    : > /tmp/scanpy-ldd.txt; \
    : > /tmp/scanpy-extensions.txt; \
    ldd "$(command -v python)" >> /tmp/scanpy-ldd.txt 2>&1; \
    python -c 'import h5py._errors, igraph._igraph, leidenalg._c_leiden, matplotlib._path, numba._helperlib, numpy._core._multiarray_umath, scipy._lib._ccallback_c, skmisc.loess._loess; print("\n".join(m.__file__ for m in (h5py._errors, igraph._igraph, leidenalg._c_leiden, matplotlib._path, numba._helperlib, numpy._core._multiarray_umath, scipy._lib._ccallback_c, skmisc.loess._loess) if ".so" in m.__file__))' \
      > /tmp/scanpy-extensions.txt; \
    test -s /tmp/scanpy-extensions.txt; \
    while IFS= read -r extension; do \
      test -s "$extension"; \
      ldd "$extension" >> /tmp/scanpy-ldd.txt 2>&1; \
    done < /tmp/scanpy-extensions.txt; \
    if grep -F 'not found' /tmp/scanpy-ldd.txt; then exit 1; fi; \
    rm -f /tmp/scanpy-extensions.txt /tmp/scanpy-ldd.txt; \
    rm -rf /tmp/numba-cache /tmp/xdg-cache /root/.cache; \
    test -z "$(find /opt/scanpy -type f \( -name '*.pyc' -o -name '*.pyo' \) -print -quit)"

# Scanpy resolves its settings relative to cwd even for a read-only invocation.
# The wrapper selects the user's work directory; direct non-root callers need a traversable default.
WORKDIR /tmp

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=scanpy
