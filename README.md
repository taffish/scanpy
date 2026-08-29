# scanpy

`scanpy` packages the official Scanpy 1.12.4 CPU Python environment for
TAFFISH.

Package identity:

- name: `scanpy`
- command: `taf-scanpy`
- kind: `tool`
- version: `1.12.4-r1`
- image: `ghcr.io/taffish/scanpy:1.12.4-r1`
- platforms: native `linux/amd64` and `linux/arm64`
- app license: Apache-2.0
- upstream: [scverse/scanpy 1.12.4](https://github.com/scverse/scanpy/releases/tag/1.12.4)

## Installation

Install this exact release from the TAFFISH Hub:

```sh
taf install scanpy 1.12.4-r1
```

## What This App Packages

Scanpy is a Python toolkit for single-cell gene-expression analysis using the
AnnData data model. This image installs the official 1.12.4 wheel with the
official `leiden` and `skmisc` extras:

- `igraph` and `leidenalg` for Leiden clustering;
- `scikit-misc` for `highly_variable_genes(..., flavor="seurat_v3")`;
- `openpyxl` and `et_xmlfile` for the public `datasets.moignard15()` XLSX
  reader;
- the core AnnData, NumPy, SciPy, pandas, h5py, scikit-learn, matplotlib,
  seaborn, statsmodels, UMAP, pynndescent, numba, and networkx stack.

The identities and checksums of the exact upstream wheel, source commit,
pinned Python base-image index, and exact `scikit-misc` source archive used on
both architectures are recorded under `/opt/scanpy/share/doc/scanpy/` in the
image. Upstream licenses—including the separate scikit-misc LOESS notice—and
the installed dependency receipt are retained there as well.

## Scope

This app supports:

- local AnnData/H5AD and 10x-style input through the Scanpy Python API;
- preprocessing, quality-control calculations, PCA, neighbors, Leiden
  clustering, marker testing, and common transformations;
- headless static plotting through matplotlib's `Agg` backend;
- the built-in `scanpy settings` command and TAFFISH command mode for packaged
  executables such as `python`, `python3`, and `pip`.

This app does not package JupyterLab, a notebook server, UCSC Cell Browser,
RAPIDS-singlecell/CUDA, downloaded example datasets inside the image, reference
atlases, model weights, cloud credentials, or every optional Scanpy integration
extra. It does package `scanpy-prepare-datasets` for the explicitly supported
resource members described below.

## Usage

Show TAFFISH wrapper help and identity:

```sh
taf-scanpy --help
taf-scanpy --version
```

Show the upstream Scanpy CLI help and settings:

```sh
taf-scanpy -- --help
taf-scanpy scanpy settings
```

Run a local analysis script:

```sh
taf-scanpy python analysis.py input.h5ad output.h5ad
```

Inspect the packaged Scanpy version:

```sh
taf-scanpy python -c '"import importlib.metadata as md; print(md.version(\"scanpy\"))"'
```

The outer literal quotes in the `python -c` example are intentionally passed
through TAFFISH automatic command mode. Prefer a script file for multiline
analysis.

## Minimal Analysis Script

Save this as `analysis.py`:

```python
import sys

import scanpy as sc

input_h5ad, output_h5ad = sys.argv[1:3]
adata = sc.read_h5ad(input_h5ad)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
adata.write_h5ad(output_h5ad)
```

Then run:

```sh
taf-scanpy python analysis.py input.h5ad normalized.h5ad
```

This path is offline when the script and input are present locally.

## Command Mode

The default upstream command is `scanpy`. TAFFISH wrapper-level option-leading
arguments can be passed after `--`; non-option-leading commands use automatic
command mode:

```sh
taf-scanpy -- --help
taf-scanpy scanpy settings
taf-scanpy python script.py
taf-scanpy pip list
```

The upstream `scanpy` CLI is not a complete analysis CLI. It provides the
built-in `settings` command and can delegate to separately installed
`scanpy-*` executables. The external `scanpy-scripts` project is not bundled:
its current published constraints target an older Scanpy/SciPy stack and are
not evidence of compatibility with this Python 3.12 release.

## Inputs and Outputs

Typical inputs include Python scripts, `.h5ad`, 10x Matrix Market directories,
10x HDF5, `.mtx`, `.csv`, `.tsv`, and formats accepted by the selected
Scanpy/AnnData reader whose optional dependency is packaged. `.loom` reading
requires the separate `loompy` dependency, which is not included in this
release. Project data and references remain user inputs unless they are one of
the explicitly prepared and verified example-dataset members described below.

Outputs are chosen by the script: processed `.h5ad` objects, TSV/CSV tables,
PNG/SVG/PDF figures, standard output, and logs. This tool app does not impose
an output directory or overwrite policy; use explicit output paths.

## Backend and Acceleration Boundaries

Ordinary CPU scripts use the same installed wrapper command on Docker, Podman,
and Apptainer. No app-intrinsic device, port, network, or platform-emulation
argument is required.

GPU analysis is unsupported in this image on all three backends because the
RAPIDS-singlecell/CUDA Python stack is not installed. Docker or Podman GPU
flags cannot add the missing packages, and Apptainer `--nv` only exposes host
NVIDIA libraries. Use a separately validated RAPIDS-singlecell environment
instead. This follows upstream's current recommendation to use
[RAPIDS-singlecell](https://rapids-singlecell.readthedocs.io/) rather than the
deprecated core Scanpy RAPIDS paths.

No browser or notebook service is exposed on Docker, Podman, or Apptainer, so
there is no port mapping, URL, SSH tunnel, readiness, or service lifecycle in
this app. Write an `.h5ad` file and use a separately packaged viewer such as
`taf-cellxgene`, or evaluate a dedicated Jupyter/Cell Browser service with its
own authentication, port, signal, and GUI checks.

## Dataset and Network Resource Audit

Core analysis does not require a model, taxonomy, reference database, or
external dataset. Optional examples are governed as independent resource
members rather than as one undifferentiated Scanpy bundle:

| Resource surface | TAFFISH 1.12.4-r1 treatment |
| --- | --- |
| `blobs` | Generated locally; no download or shared resource. |
| `krumsiek11`, `toggleswitch`, `pbmc68k_reduced` | Already distributed inside the official Scanpy wheel; no separate helper action. |
| `burczynski06`, `pbmc3k-raw`, `pbmc3k-processed` | Fixed URL, byte size and SHA256 are recorded in the packaged catalog; `scanpy-prepare-datasets` may download and verify these exact members. |
| `moignard15`, `paul15` | Authorized-local-import-only. The helper verifies the expected fixed file but does not download or confer redistribution rights. |
| Visium sample family | Not accepted by the fixed helper: the Scanpy API is deprecated in favor of Squidpy and the evolving family has no app-pinned member/license inventory. Prefer an authorized local sample or reviewed Squidpy app; an explicit persistent unverified-download route is available below. |
| EBI Expression Atlas accessions | Not accepted by the fixed helper because accession responses evolve and this release has no immutable response digest. Use a frozen local response when reproducibility matters; an explicit persistent unverified-download route is available below. |
| `scanpy.queries` | Unsupported in this image because the optional `pybiomart` and `gprofiler-official` clients are absent; those services also evolve independently of this release. |

The classification follows the public
[Scanpy 1.12.4 dataset source](https://github.com/scverse/scanpy/blob/1.12.4/src/scanpy/datasets/_datasets.py).
The fixed catalog SHA256 is
`7ec2711c801966b85eafae96857a166a70dbc8921a9094b627d65d9aad5f70fd`.
The audited member identities are:

| Member/file | Bytes | SHA256 |
| --- | ---: | --- |
| wheel `krumsiek11.txt` | 59,808 | `a49c6d04bd77f61028133a9b787222ebf00c4fc02dbf8e2b8edda493a0d5dc93` |
| wheel `toggleswitch.txt` | 4,200 | `11b70a557b9a9c942ba15f8c89d070d914d373d3e76f91f4472c5d8e14dc74e2` |
| wheel `10x_pbmc68k_reduced.h5ad` | 1,911,295 | `863e19914ab2d4ba97edc9623ac3a343c0461f1e40b121bfb5fa92638b22e9bd` |
| `burczynski06` | 16,295,674 | `86126c1a3c163ea20abb14c1a9711aaff34e6c492ef6dd86298bbaf18cc3f5f3` |
| `pbmc3k-raw` | 5,855,727 | `89a96f1beaa2dd83a687666d3f19a4513ac27a2a2d12581fcd77afed7ea653a1` |
| `pbmc3k-processed` | 24,653,425 | `0db367b991dd95809732b218539ede489bea99113807f62ebd7ccc970025fe38` |
| `moignard15` | 3,402,603 | `e7b358fef2b6da115b7ee3ab4c7fc55fd80e210bba427902e4afc9118992747c` |
| `paul15` | 10,297,693 | `6161984f758dd464992edc23f1a8ab89b2081600130c6aa93a1ab12b3ada5bfb` |

List the supported members and inspect a non-writing plan:

```sh
taf-scanpy scanpy-prepare-datasets --list-datasets
taf-scanpy scanpy-prepare-datasets --inventory
taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run
```

The dry-run reports `required_free_bytes`. Preparation requires at least the
larger of 0.05 GiB and three times the selected member size; an administrator
may raise that floor with `--min-free-gb` for local storage policy.

Prepare one or more automatically downloadable members in the personal root:

```sh
ROOT="$HOME/.local/share/taffish/datasets/scanpy"
mkdir -p "$ROOT"
TAFFISH_SCANPY_ALLOW_NETWORK=1 \
TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
```

The selector is intentionally exact-one. Repeat the command for
`burczynski06` or `pbmc3k-processed`; each successful invocation preserves the
verified members already present and adds the selected member. The network
opt-in is accepted only while a persistent install parent is mounted; it does
not turn an ordinary analysis invocation into an implicit download session.

`TAFFISH_SCANPY_DATASET_INSTALL_ROOT` is a host parent directory mounted
read-write only for explicit preparation. Inside the container it is
`/dataset-install`; the helper atomically prepares the version root
`/dataset-install/1.12.4`, records the catalog identity and per-member hashes,
and supports an explicit verification pass:

```sh
TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --verify-only \
  --dataset-root /dataset-install/1.12.4
```

The helper serializes writers with a version lock and keeps resumable download
cache state under the mounted parent. Each exact-member update is staged
privately; the previous member and root receipts are backed up, the root READY
receipt is written last, and ordinary exceptions or Ctrl-C restore the prior
tree before returning failure. `--force` repairs only the selected member and
does not authorize changing any other catalog member. Verification rejects
partial members, unknown files/directories, symlinks, mismatched hashes and
receipt drift.

If the helper reports `retained failed transaction for recovery`, stop using
that root, keep the reported transaction directory, and make a host-side
snapshot before repair. Disable discovery during both verification and repair:

```sh
TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 \
TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets --verify-only \
  --dataset-root /dataset-install/1.12.4
```

If verification fails, prefix the same exact `--dataset ... --force`
preparation command with `TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0` and review the
selected source/cache first. Once deep verification succeeds and no helper process is active, an
administrator may archive or remove the retained transaction. Do not delete it
before verification because it can contain the only rollback copy.

After deep verification succeeds and no helper process is active, an
administrator may also remove the selected member's resumable cache file under
`$ROOT/.taffish-scanpy/cache/1.12.4/` (`.source` or `.part`) to reclaim space;
do not remove a retained failed transaction. A later download will need network
access again.

`moignard15` and `paul15` are never downloaded by the helper. Obtain the exact
file through a route and terms that authorize your use and place it under the
host install parent's `imports/` directory. For Moignard, for example:

```sh
mkdir -p "$ROOT/imports"
# Independently place the authorized file at $ROOT/imports/nbt.3154-S3.xlsx.
TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
  taf-scanpy scanpy-prepare-datasets \
  --dataset moignard15 \
  --source-file /dataset-install/imports/nbt.3154-S3.xlsx \
  --confirm-authorized-local-import
```

`paul15` follows the same exact-one pattern with
`--source-file /dataset-install/imports/paul15.h5`. The helper's checksum check
proves identity, not permission; the caller remains responsible for
authorization.

For one site copy, an administrator prepares either
`/usr/local/share/taffish/datasets/scanpy/1.12.4` or
`/opt/taffish/datasets/scanpy/1.12.4`, verifies it, then makes the completed
tree root-owned and read-only for ordinary users. A representative setup is:

```sh
sudo mkdir -p /usr/local/share/taffish/datasets/scanpy
sudo chown "$(id -u):$(id -g)" /usr/local/share/taffish/datasets/scanpy
TAFFISH_SCANPY_ALLOW_NETWORK=1 \
TAFFISH_SCANPY_DATASET_INSTALL_ROOT=/usr/local/share/taffish/datasets/scanpy \
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
sudo chown -R root:root /usr/local/share/taffish/datasets/scanpy/1.12.4
sudo chmod -R a+rX /usr/local/share/taffish/datasets/scanpy/1.12.4
sudo chown root:root /usr/local/share/taffish/datasets/scanpy
```

This is the administrator-once/ordinary-user-read-only contract; a production
site installation was not exercised on this development host. Docker normally
creates prepared files as container root; ordinary users can read the final
`a+rX` tree, while an administrator must perform later cleanup or forced
replacement. Rootless Podman and Apptainer normally retain caller ownership.

For analysis, the wrapper discovers a complete prepared root in this order:
explicit `TAFFISH_SCANPY_DATASET_PATH`, the personal path, `/usr/local`, then
`/opt`. It mounts the selected version root read-only at `/datasets/scanpy` and
sets both the resource-root identity and Scanpy's `settings.datasetdir`
automatically. `TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0` disables both discovery
and the explicit prepared-root mount. An explicit path that is missing,
partial, modified, or contains symlinks fails closed before the container can
use it rather than silently falling back or downloading a replacement.

Host install, prepared-root, and unverified-download paths must not contain
whitespace, commas, colons, or the glob characters `*`, `?`, `[` and `]`;
those characters cannot be represented safely and uniformly in Docker/Podman
volume and Apptainer bind runtime arguments. The wrapper rejects them before
starting a container.

The shortest backend-specific wrapper forms are:

```sh
TAFFISH_CONTAINER_BACKEND=docker taf-scanpy python analysis.py
TAFFISH_CONTAINER_BACKEND=podman taf-scanpy python analysis.py
TAFFISH_CONTAINER_BACKEND=apptainer taf-scanpy python analysis.py
```

Docker and Podman prepared-root behavior is a required runtime validation gate
before publish. Apptainer uses the same wrapper contract but is compile-checked
only on this host because no Apptainer runtime is installed.

Docker and Podman run ordinary wrapper invocations with `--network=none` by
default. On all backends the packaged Python policy also blocks implicit
Scanpy example downloads before network access. If automatic mounting is
unsuitable, disable it and bind a verified version root manually as read-only:

```sh
docker run --rm -v "$PWD:/work" -w /work \
  --network none \
  -v /host/scanpy/1.12.4:/datasets/scanpy:ro \
  -e TAFFISH_SCANPY_DATASET_ROOT=/datasets/scanpy \
  -e TAFFISH_SCANPY_DATASETDIR=/datasets/scanpy \
  ghcr.io/taffish/scanpy:1.12.4-r1 python analysis.py
podman run --rm -v "$PWD:/work" -w /work \
  --network none \
  -v /host/scanpy/1.12.4:/datasets/scanpy:ro \
  -e TAFFISH_SCANPY_DATASET_ROOT=/datasets/scanpy \
  -e TAFFISH_SCANPY_DATASETDIR=/datasets/scanpy \
  ghcr.io/taffish/scanpy:1.12.4-r1 python analysis.py
apptainer exec --bind /host/scanpy/1.12.4:/datasets/scanpy:ro \
  --env TAFFISH_SCANPY_DATASET_ROOT=/datasets/scanpy,TAFFISH_SCANPY_DATASETDIR=/datasets/scanpy \
  docker://ghcr.io/taffish/scanpy:1.12.4-r1 python analysis.py
```

When an EBI accession or legacy Visium example truly must be fetched directly,
use a separate persistent directory and the explicit double opt-in. Unset both
prepared-resource selectors in the same invocation:

```sh
ONLINE_ROOT="$PWD/scanpy-unverified-downloads"
mkdir -p "$ONLINE_ROOT"
unset TAFFISH_SCANPY_DATASET_PATH TAFFISH_SCANPY_DATASET_INSTALL_ROOT
export TAFFISH_SCANPY_ALLOW_NETWORK=1
export TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS=1
export TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT="$ONLINE_ROOT"
TAFFISH_CONTAINER_BACKEND=docker taf-scanpy python online.py
TAFFISH_CONTAINER_BACKEND=podman taf-scanpy python online.py
TAFFISH_CONTAINER_BACKEND=apptainer taf-scanpy python online.py
unset TAFFISH_SCANPY_ALLOW_NETWORK TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS
unset TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT
```

The wrapper mounts that directory read-write at `/dataset-download`; these
responses have no app-fixed checksum, stable member inventory, or uniform
resource license and are therefore deliberately marked unverified and
nonreproducible. Freeze and independently authorize the resulting files before
scientific reuse. Docker/Podman are required runtime gates; the Apptainer form
is a compile-checked contract only on this host.

Local-input analysis remains offline. Other Python libraries can implement
their own network clients, so the Scanpy fail-closed policy is not a general
container firewall on Apptainer; use site network isolation when required.

## GUI and Companion Routing

The 1.12.4 package declares only `scanpy = scanpy.cli:console_main`; its
`Framework :: Jupyter` classifier does not install a notebook or server.
Jupyter is therefore a separate long-running service boundary, not a hidden
GUI in this image.

`scanpy.external.exporting.cellbrowser()` is a public integration that imports
the independent `cellbrowser` package, can build browser assets, and can start
an HTTP server. That package and its static/service runtime are intentionally
not included in this core app. A future Cell Browser app must own generator,
port, localhost security, readiness, logs, Ctrl-C/TERM cleanup, backend, and
browser validation. `spring_project()` only exports project files; its viewer
also remains external. Consequently the current app exposes no GUI surface,
and GUI runtime checks are N/A after this explicit routing decision rather than
because the optional integrations were overlooked.

## Optional Integration Boundaries

The image includes the `leiden` and `skmisc` extras plus fixed
`openpyxl`/`et_xmlfile` support for the public `datasets.moignard15()` XLSX
reader. It does not include `loompy`, `bbknn`, Dask/Dask-ML, Harmony, MAGIC,
legacy Louvain, the plotting color extra, RAPIDS, Scanorama, Scrublet's
optional threshold dependency, or other integration packages. Additions should
be made as a new release or dedicated app after dependency, architecture,
license, and smoke review; mutating the published environment with `pip
install` is not a reproducible workflow.

The 1.12.4 Scrublet bug fix is therefore upstream behavior outside this
release's packaged extra and is not claimed as tested here.

## Troubleshooting

- `No module named scanpy`: run the script with `taf-scanpy python ...`, not
  the host Python.
- `scanpy: invalid choice`: core analysis uses the Python API; the built-in CLI
  only guarantees `settings` unless a compatible `scanpy-*` companion exists.
- A prepared member is not found: prepare or select a validated version root;
  the wrapper binds `sc.settings.datasetdir` automatically. An explicit root
  that is partial, modified, orphaned, unreadable or contains a symlink is
  rejected instead of falling back.
- A fixed example is missing: use `scanpy-prepare-datasets` for
  `burczynski06`, `pbmc3k-raw`, or `pbmc3k-processed`; import `moignard15` or
  `paul15` only from an independently authorized local copy.
- A Visium or EBI call is blocked: prefer an authorized frozen local input, or
  use the documented persistent double opt-in and treat the result as
  unverified. Fixed helper members remain blocked on that route. Query clients
  are not installed.
- `retained failed transaction for recovery`: preserve the named directory,
  snapshot the host parent, set `TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0`, verify the
  root, and repair only the same exact member as described above.
- A GPU, Jupyter, or Cell Browser command is missing: those runtimes are not
  packaged in this CPU/headless app.
- Large H5AD matrices, neighbor graphs, dense conversions, and plots can need
  substantial RAM, CPU, temporary space, and output storage.

## Testing

The independent offline smoke contract covers exact package/provenance
identity, the built-in CLI/settings surface, direct imports, and three 1.12.4
regressions: dense/CSR normalization with zero-count cells, CSR normalization
with `NUMBA_DISABLE_JIT=1`, and stable boolean-category colors after
subsetting. A synthetic workflow covers Seurat-v3 HVG selection,
normalization/logging, PCA, neighbors, Leiden, marker testing, H5AD/TSV output,
and a static PNG.

Dockerfile build-time checks run only identity, imports, ordinary help/settings,
the normalization/color and offline Moignard XLSX probes, helper catalog and
dry-run checks, and a reduced non-rendering workflow. Graph clustering, marker
testing, static rendering, and real resource transfer remain runtime checks so
an arm64 build is not gated by brittle rendering, network, or JIT-heavy work.

Resource publish validation separately checks selector rejection, automatic
download retry/resume and exact SHA, authorized local import, transaction and
Ctrl-C rollback, corrupt/partial/orphan/symlink rejection, manifest/inventory
identity, install-root confinement, prepared-root discovery, ordinary-user
read-only reuse, and the EBI/Visium-only unverified policy. These fixtures do
not claim a privileged production site installation.

These tests do not establish scientific correctness on production data,
production-scale performance, online dataset integrity, every optional extra,
GPU behavior, or a GUI/browser service.

## License and Citation

TAFFISH app packaging is Apache-2.0. Scanpy and scikit-misc remain
BSD-3-Clause; openpyxl and et_xmlfile are MIT. Their license texts and the
separately required AT&T Cleveland/Grosse/Shyu LOESS notice are retained under
`/opt/scanpy/share/doc/scanpy/`.

The Burczynski source is NCBI GEO; GEO states that NCBI places no restrictions
on use or distribution while warning that submitters may retain intellectual
property rights ([GEO disclaimer](https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html)).
The 10x PBMC3k source is published under CC BY 4.0
([10x dataset page](https://www.10xgenomics.com/datasets/3-k-pbm-cs-from-a-healthy-donor-1-standard-1-1-0)).
Moignard and Paul are local-import-only because the reviewed source evidence
does not grant this app a general automated redistribution right
([Moignard source](https://www.nature.com/articles/nbt.3154),
[Paul source](https://pubmed.ncbi.nlm.nih.gov/26627738/)). EBI Expression Atlas
website material is CC BY 4.0, but accession contents retain original-owner
rights and may change independently
([EBI license](https://www.ebi.ac.uk/gxa/licence.html),
[EBI terms](https://www.ebi.ac.uk/about/terms-of-use/)). These scientific
resources and online services are not relicensed by the software licenses.

Cite Scanpy according to upstream guidance:

Wolf FA, Angerer P, Theis FJ. “SCANPY: large-scale single-cell gene expression
data analysis.” *Genome Biology* 19, 15 (2018).
[doi:10.1186/s13059-017-1382-0](https://doi.org/10.1186/s13059-017-1382-0),
PMID 29409532.
