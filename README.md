# Scanpy 1.13.0 for TAFFISH

Run [Scanpy 1.13.0](https://github.com/scverse/scanpy/releases/tag/1.13.0) on local single-cell expression data. This CPU tool packages the upstream Python API and its small CLI. It supports the default Matplotlib figures and the upstream **ScanpyV2Preview** plotting API, including interactive HTML files that open offline. It does not start a notebook, web server or desktop.

## Install and run

Install the exact version from the Hub:

```sh
taf install scanpy 1.13.0-r1
taf-scanpy --version
taf-scanpy -- --help
taf-scanpy scanpy settings
taf-scanpy python analysis.py input.h5ad normalized.h5ad
```

The upstream CLI mostly exposes settings, not an analysis language. Put analysis code in a Python script. For example, save this as `analysis.py`:

```python
import sys
import scanpy as sc

data = sc.io.read_h5ad(sys.argv[1])
sc.pp.normalize_total(data, target_sum=10_000)
sc.pp.log1p(data)
data.write_h5ad(sys.argv[2])
```

The wrapper's automatic command mode requires literal quoting around arguments with spaces: `taf-scanpy python analysis.py "'input with spaces.h5ad'" "'normalized cells.h5ad'"`. Give each output a new name; the analysis script controls overwriting. For Docker, Podman or Apptainer, select `TAFFISH_CONTAINER_BACKEND=docker`, `podman` or `apptainer` before the same command.

## Plots: static figures or a standalone interactive file

Default settings retain the Scanpy 1.x Matplotlib backend. Save PNG, SVG or PDF in the script (use `show=False`). To export the **upstream** preview plot, save this instead as `plot.py` and run `taf-scanpy python plot.py`:

```python
from pathlib import Path
import holoviews as hv
from bokeh.embed import file_html
from bokeh.model import Model
from bokeh.resources import INLINE
import scanpy as sc

data = sc.datasets.pbmc68k_reduced()  # distributed with the wheel
with sc.settings.override(preset=sc.Preset.ScanpyV2Preview):
    sc.pl.hv_init("bokeh")
    sc.pp.pca(data, n_comps=3)
    plot = sc.pl.pca(data).opts(tools=["hover", "box_zoom", "reset", "save"],
                                aspect=None, data_aspect=None, responsive=True,
                                height=420, title="Scanpy PCA")
    figure = hv.render(plot, backend="bokeh")
    assert all(type(m).__module__.startswith("bokeh.") for m in figure.references())
    Model.clear_extensions()
    Path("pca.html").write_text(file_html(figure, INLINE, "Scanpy PCA"), encoding="utf-8")
```

Open `pca.html` on the host, including without internet access. The script exports the original figure, not a screenshot: hover, box zoom, reset and PNG export remain available. Use a separate export script: after checking that this figure uses only built-in Bokeh models, it clears unused extension registrations before embedding the assets. A generic `hv.save(..., resources=INLINE)` export can still reference optional Panel styles and icons. Do not clear extensions on a dashboard that actually uses them. No port, server, SSH tunnel or GPU flag is needed on any backend.

The preview is an **opt-in analysis preset**, not just a theme: it can change defaults, result keys and numerical results. Use a separate object or script when comparing with the default. The HTML embeds plotted data and may include the export working-directory path in plotting-library metadata. Use a neutral working directory and check the file before sharing. Jupyter, Cell Browser, SPRING and GPU/RAPIDS environments remain independent; the CPU image and backend flags do not provide them.

## Example data: optional, versioned and read-only during analysis

Local H5AD/10x inputs need no external database or downloaded model. Generated and wheel-bundled examples work offline. Five optional fixed files are described by the [catalog](docker/scanpy-resource-catalog.json) and [upstream registry](https://github.com/scverse/scanpy/blob/1.13.0/src/scanpy/datasets/registry.yaml).

| Member | Acquisition and rights |
| --- | --- |
| `pbmc3k-raw`, `pbmc3k-processed` | Explicit download or verified local import; credit 10x Genomics (CC BY 4.0). |
| `burczynski06` | Explicit download or verified local import; retain GEO accession GDS1615 and submitter attribution. |
| `moignard15`, `paul15` | Authorized local import only. A checksum is not a license; no automatic download or redistribution. |

Inspect sizes, digests, licensing and free-space requirements without writing anything:

```sh
taf-scanpy scanpy-prepare-datasets --inventory
taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run
```

**Personal setup.** Choose an existing local filesystem with adequate free space. Resource-root paths cannot contain whitespace, commas, colons or shell glob characters. For rootless Podman or Apptainer, change the backend selector; commands and in-container paths are the same.

```sh
ROOT="$HOME/.local/share/taffish/datasets/scanpy"
mkdir -p "$ROOT"
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 \
  TAFFISH_SCANPY_ALLOW_NETWORK=1 TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --verify-only --dataset-root /dataset-install/1.13.0
```

To reuse a verified 1.12.5 file, leave the old tree and receipts untouched. If both version directories use the same install parent, the new helper can read the old file offline:

```sh
TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw \
  --source-file /dataset-install/1.12.5/pbmc3k_raw.h5ad
```

For a separate install parent, put the authorized file under `$ROOT/imports` and pass `/dataset-install/imports/FILENAME`. The three changed destination names are `burczynski06.soft.gz`, `moignard15.xlsx` and `paul15.h5`; the two PBMC names and all five digests are unchanged. Add `--confirm-authorized-local-import` **only** for Moignard or Paul. Repeat per exact member; there is no implicit full collection install.

**System setup (Linux).** A site administrator can prepare one shared version tree. Run the following in an administrator shell with access to the installed wrapper and Docker; this never requires making an ordinary user a Docker administrator:

```sh
SITE=/usr/local/share/taffish/datasets/scanpy
install -d -m 0755 "$SITE"
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 \
  TAFFISH_SCANPY_ALLOW_NETWORK=1 TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$SITE" \
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 \
  TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$SITE" taf-scanpy scanpy-prepare-datasets \
  --verify-only --dataset-root /dataset-install/1.13.0
chmod -R a+rX,go-w "$SITE/1.13.0"
```

The prepared tree and its parent must remain controlled by the administrator, not writable by ordinary readers. Ensure all parent directories allow traversal. For analysis, do **not** set the writable install-root variable. Discovery order: explicit `TAFFISH_SCANPY_DATASET_PATH`, personal root, `/usr/local/share/taffish/datasets/scanpy/1.13.0`, then `/opt/taffish/datasets/scanpy/1.13.0`. Readers mount the selected version root read-only at `/datasets/scanpy`. A valid host alias to a complete root is allowed; broken aliases, internal symlinks, mismatched receipts, unknown or corrupt files fail. Set `TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0` to disable discovery. Analysis never implicitly repairs or replaces a library.

**Recovery.** A repeated install of an intact member is a no-op. Review a failed verification before requesting `--force` for **that exact member** with a known source and auto-mount disabled; preserve diagnostic/recovery directories. A prior valid copy and other members must survive a failed transaction. Do not rename a 1.12.5 tree to 1.13.0 or remove old staging directories to silence an error.

**Evolving online sources.** EBI accessions and legacy Visium samples are not part of the fixed catalog. For an explicitly authorized request, select a separate, persistent, writable download root. Unset both `TAFFISH_SCANPY_DATASET_PATH` and `TAFFISH_SCANPY_DATASET_INSTALL_ROOT`, then run:

```sh
ONLINE_ROOT="$PWD/scanpy-online"; mkdir -p "$ONLINE_ROOT"
TAFFISH_SCANPY_ALLOW_NETWORK=1 TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS=1 \
  TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT="$ONLINE_ROOT" taf-scanpy python online.py
```

The same invocation works on all three backends. Fixed members still require the helper; do not assume a response is licensed for sharing or will be reproduced later. The policy governs Scanpy's built-in example clients, not arbitrary Python networking. Docker/Podman analysis is network-disabled by default; request site-level isolation if needed for other Python libraries on Apptainer.

## Packaging, compatibility and provenance

This is `ghcr.io/taffish/scanpy:1.13.0-r1` for native Linux amd64 and arm64. It uses the official, hash-pinned BSD-3-Clause wheel, Python 3.13, the Leiden and preview dependencies, upstream scikit-misc built from verified source (including ARM64), and openpyxl for the spreadsheet reader. The TAFFISH wrapper is Apache-2.0. Software licenses do not relicense external datasets. See [release notes](https://scanpy.scverse.org/en/stable/release-notes/#v1-13-0) and [citation](https://doi.org/10.1186/s13059-017-1382-0).

Scanpy 1.13 adds the `scanpy.io` API, optional `anndata.acc` input/output accessors and preview visualizations. Use `mask`/accessors instead of removed `use_highly_variable`; the removed RAPIDS flavors are not restored. The normal API and scientific algorithms come from the upstream wheel. The packaging only maps authorized example data to validated local files and gates network access. Optional third-party query clients, independent viewers and cloud services are not part of this release.

The image records package versions and source checksums under `/opt/scanpy/share/doc/scanpy/`; use `taf-scanpy pip list` to inspect them. The pinned base digest, primary wheel and selected dependencies identify these inputs. Debian mirrors and transitive PyPI packages can change: this is not a promise that a fresh future build is byte-identical.

The native Docker images measure 867,061,286 bytes on amd64 and 901,936,889 bytes on arm64 (uncompressed); the amd64 SIF is 278,519,808 bytes. Compared with the corresponding 1.12.5-r1 measurements, the increase is about 111 MiB per architecture, across both the Python upgrade and the preview dependencies. On arm64, LLVM (`llvmlite`) alone takes 168 MiB; Panel, Bokeh and HoloViews use about 66, 30 and 16 MiB, respectively. These are installed sizes, not registry download sizes.
