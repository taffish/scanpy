#!/usr/bin/env python3
"""Small offline Scanpy workflow used by Dockerfile and TAFFISH smoke tests."""

from __future__ import annotations

import importlib.metadata as metadata
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData


def make_adata() -> AnnData:
    rng = np.random.default_rng(7)
    counts = rng.poisson(lam=1.0, size=(24, 30)).astype(np.float32)
    counts[:12, :6] += rng.poisson(lam=3.0, size=(12, 6)).astype(np.float32)
    counts[12:, 6:12] += rng.poisson(lam=3.0, size=(12, 6)).astype(np.float32)

    adata = AnnData(counts)
    adata.obs_names = [f"cell_{i:02d}" for i in range(adata.n_obs)]
    adata.var_names = [f"gene_{i:02d}" for i in range(adata.n_vars)]
    adata.obs["group"] = pd.Categorical(["A"] * 12 + ["B"] * 12)
    adata.layers["counts"] = adata.X.copy()
    return adata


def main() -> int:
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("scanpy-smoke-out")
    outdir.mkdir(parents=True, exist_ok=True)

    adata = make_adata()

    sc.pp.filter_cells(adata, min_counts=1)
    sc.pp.filter_genes(adata, min_cells=1)
    hvg = sc.pp.highly_variable_genes(
        adata,
        layer="counts",
        flavor="seurat_v3",
        n_top_genes=10,
        inplace=False,
    )
    if int(hvg["highly_variable"].sum()) != 10:
        raise RuntimeError("Seurat v3 highly-variable gene smoke failed")

    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    adata.raw = adata
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=5, svd_solver="arpack", random_state=7)
    sc.pp.neighbors(adata, n_neighbors=5, n_pcs=5, random_state=7)
    sc.tl.leiden(
        adata,
        resolution=0.5,
        random_state=7,
        key_added="leiden",
        flavor="igraph",
        n_iterations=2,
        directed=False,
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in log2",
            category=RuntimeWarning,
        )
        sc.tl.rank_genes_groups(adata, groupby="group", method="t-test", use_raw=True)

    markers = sc.get.rank_genes_groups_df(adata, group="A")
    if markers.empty:
        raise RuntimeError("rank_genes_groups smoke produced no marker table")
    markers.head(10).to_csv(outdir / "markers.tsv", sep="\t", index=False)

    sc.pl.pca(adata, color="group", show=False)
    plt.savefig(outdir / "pca.png", dpi=120, bbox_inches="tight")
    plt.close("all")

    adata.write_h5ad(outdir / "scanpy_smoke.h5ad")

    versions = [
        ("python", ".".join(map(str, sys.version_info[:3]))),
        ("scanpy", metadata.version("scanpy")),
        ("anndata", metadata.version("anndata")),
        ("numpy", metadata.version("numpy")),
        ("scipy", metadata.version("scipy")),
        ("scikit-learn", metadata.version("scikit-learn")),
        ("leidenalg", metadata.version("leidenalg")),
        ("scikit-misc", metadata.version("scikit-misc")),
    ]
    pd.DataFrame(versions, columns=["package", "version"]).to_csv(
        outdir / "versions.tsv",
        sep="\t",
        index=False,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
