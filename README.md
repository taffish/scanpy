# scanpy

TAFFISH wrapper for [Scanpy](https://scanpy.readthedocs.io/) 1.12.3, the
scverse Python toolkit for scalable single-cell gene-expression analysis.

## Package Identity

- name: `scanpy`
- command: `taf-scanpy`
- kind: `tool`
- TAFFISH version: `1.12.3-r1`
- container image: `ghcr.io/taffish/scanpy:1.12.3-r1`
- upstream: `scverse/scanpy` tag `1.12.3`
- runtime: Python 3.12 with Scanpy 1.12.3
- app license: Apache-2.0
- upstream license: BSD-3-Clause

## What Is Included

This image installs Scanpy from PyPI with the common optional extras used by
standard offline workflows:

- `scanpy[leiden]` for `igraph` and `leidenalg` clustering support.
- `scanpy[skmisc]` for Seurat v3 highly-variable gene selection.
- Core Scanpy dependencies such as AnnData, NumPy, SciPy, pandas,
  scikit-learn, h5py, matplotlib, seaborn, statsmodels, UMAP, pynndescent,
  numba, and networkx.

The image does not bundle large reference atlases, model weights, notebooks,
project datasets, or online services.

Scanpy 1.12.3 fixes Dask aggregation for selected function lists, corrects
query centering during `scanpy.tl.ingest` PCA projection, and improves
`rank_genes_groups` `vs_rest` performance. The packaged extras and command
surface are unchanged from the TAFFISH 1.12.2 runtime.

## Usage

Show the TAFFISH package help:

```sh
taf-scanpy --help
```

Show the upstream Scanpy CLI help:

```sh
taf-scanpy -- --help
taf-scanpy scanpy --help
```

Run a Python one-liner inside the same container:

```sh
taf-scanpy python -c '"import importlib.metadata as md; print(md.version(\"scanpy\"))"'
```

Run a Scanpy analysis script:

```sh
taf-scanpy python analysis.py
```

The app keeps TAFFISH command mode enabled, so non-option-leading commands run
inside the Scanpy container. This is useful for helper commands such as:

```sh
taf-scanpy python script.py
taf-scanpy scanpy --help
taf-scanpy pip list
```

For `python -c`, keep the code string quoted as a literal argument as shown
above. For multi-line analysis, a script file or standard input is usually
clearer.

## Inputs And Outputs

Scanpy itself is a Python API, so inputs and outputs are determined by the
script or upstream CLI command you run. Typical inputs include `.h5ad`, 10x
Matrix Market directories, 10x HDF5 files, `.loom`, `.mtx`, `.csv`, `.tsv`, and
other files supported by Scanpy/AnnData readers. Typical outputs include
processed `.h5ad` files, tables such as marker-gene TSV/CSV files, and figures
written by matplotlib/Scanpy plotting calls.

TAFFISH does not impose an output directory for this tool app. Your Python
script controls where files are written; use explicit output paths when running
inside workflows.

## Minimal Example

```sh
taf-scanpy python - <<'PY'
import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData

adata = AnnData(np.array([[1, 0, 3], [0, 2, 1], [5, 0, 0]], dtype=float))
adata.obs_names = ["cell1", "cell2", "cell3"]
adata.var_names = ["geneA", "geneB", "geneC"]
adata.obs["group"] = pd.Categorical(["A", "A", "B"])

sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
adata.write_h5ad("example.h5ad")
print(adata)
PY
```

## Boundaries

r1 is an offline Scanpy runtime. It supports the core Python API and the
upstream `scanpy` console script, including common preprocessing, AnnData I/O,
PCA/neighbors, Leiden clustering, marker testing, HVG selection with
`skmisc`, and static plotting through the headless matplotlib `Agg` backend.

The image does not include optional integration packages such as `bbknn`,
`harmonypy`, `magic-impute`, `scanorama`, `scrublet`, Dask acceleration,
RAPIDS/GPU dependencies, JupyterLab, legacy `louvain`, or single-cell reference
datasets. Those can be added in future specialized apps or flows if they become
part of a stable TAFFISH workflow. Louvain is intentionally not bundled in r1
because its current PyPI path needs source-build tooling on Python 3.12; Leiden
is the packaged clustering path.

Network access is not required for the packaged smoke path. User scripts may
use the network only if the container backend and site policy allow it; online
downloads are not part of the reproducible r1 contract.

## Citation

Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression
data analysis. Genome Biology 19, 15 (2018). doi:
`10.1186/s13059-017-1382-0`; PMID: `29409532`.
