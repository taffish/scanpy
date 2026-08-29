#!/usr/bin/env python3
"""Small offline Scanpy workflow used by Dockerfile and TAFFISH smoke tests."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import sys
import tempfile
import warnings
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from scipy import sparse
from scanpy.plotting._tools.scatterplots import _get_palette


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--buildtime",
        action="store_true",
        help="skip graph, marker, and static plotting checks",
    )
    parser.add_argument(
        "--regressions-only",
        action="store_true",
        help="run the lightweight Scanpy 1.12.4 regression probes only",
    )
    parser.add_argument(
        "--policy-only",
        action="store_true",
        help="check that implicit Scanpy dataset downloads fail before network access",
    )
    parser.add_argument(
        "--unverified-policy-only",
        action="store_true",
        help="check that the explicit online route permits only EBI and Visium clients",
    )
    parser.add_argument("outdir", nargs="?", default="scanpy-smoke-out")
    return parser.parse_args()


def check_regressions() -> None:
    counts = np.array(
        [[0.0, 0.0], [4.0, 6.0], [8.0, 12.0], [12.0, 18.0]],
        dtype=np.float64,
    )
    dense = AnnData(counts.copy())
    csr = AnnData(sparse.csr_matrix(counts))

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="Some cells have zero counts", category=UserWarning
        )
        sc.pp.normalize_total(dense, exclude_highly_expressed=False)
        sc.pp.normalize_total(csr, exclude_highly_expressed=False)

    np.testing.assert_allclose(csr.X.toarray(), dense.X)
    np.testing.assert_allclose(np.asarray(csr.X.sum(axis=1)).ravel()[1:], 20.0)

    flags = AnnData(
        X=np.ones((4, 1)),
        obs={"flag": [False, True, False, True]},
        uns={"flag_colors": ["red", "blue"]},
    )
    true_subset = flags[flags.obs["flag"]].copy()
    false_subset = flags[~flags.obs["flag"]].copy()
    expected = {"False": "red", "True": "blue"}
    if _get_palette(true_subset, "flag") != expected:
        raise RuntimeError("boolean True-subset palette regression failed")
    if _get_palette(false_subset, "flag") != expected:
        raise RuntimeError("boolean False-subset palette regression failed")


def check_moignard_excel() -> None:
    """Exercise the real moignard15 XLSX reader without network access."""

    prefixes = ("HF", "NP", "PS", "4SG", "4SFG")
    cells = [f"{prefixes[index % len(prefixes)]}_cell_{index:03d}" for index in range(533)]
    genes = ("Eif2b1", "Mrpl19", "Polr2a", "Ubc", "GeneA", "GeneB")
    values = np.arange(len(cells) * len(genes), dtype=np.float32).reshape(
        len(cells), len(genes)
    )
    frame = pd.DataFrame(values, columns=genes)
    frame.insert(0, "cell", cells)

    with tempfile.TemporaryDirectory(prefix="taf-scanpy-moignard-") as temporary:
        dataset_root = Path(temporary)
        workbook = dataset_root / "moignard15" / "nbt.3154-S3.xlsx"
        workbook.parent.mkdir(parents=True)
        frame.to_excel(workbook, sheet_name="dCt_values.txt", index=False)

        original_datasetdir = sc.settings.datasetdir
        try:
            sc.settings.datasetdir = dataset_root
            with patch(
                "scanpy.readwrite._download",
                side_effect=RuntimeError("offline regression attempted a download"),
            ):
                adata = sc.datasets.moignard15()
        finally:
            sc.settings.datasetdir = original_datasetdir

    if adata.shape != (533, 2):
        raise RuntimeError(f"moignard15 XLSX shape regression failed: {adata.shape}")
    if list(adata.var_names) != ["GeneA", "GeneB"]:
        raise RuntimeError("moignard15 gene-filter regression failed")
    if not 0 <= int(adata.uns["iroot"]) < adata.n_obs:
        raise RuntimeError("moignard15 root-cell regression failed")
    if set(adata.obs["exp_groups"].astype(str)) != set(prefixes):
        raise RuntimeError("moignard15 experimental-group regression failed")


def check_dataset_policy() -> None:
    sentinel = Path(
        "/opt/scanpy/share/scanpy/TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED"
    )
    if sc.settings.datasetdir != sentinel or not sentinel.is_file():
        raise RuntimeError("TAFFISH Scanpy datasetdir fail-closed policy is not active")

    import scanpy._utils as scanpy_utils

    with tempfile.TemporaryDirectory(prefix="taf-scanpy-prepared-member-") as temporary:
        prepared = Path(temporary) / "paul15.h5"
        prepared.write_bytes(b"taffish-prepared-member-policy-probe\n")
        scanpy_utils.check_presence_download(
            prepared,
            "https://exampledata.scverse.org/scanpy/paul15.h5",
        )
        try:
            scanpy_utils.check_presence_download(
                Path(temporary) / "missing-paul15.h5",
                "https://exampledata.scverse.org/scanpy/paul15.h5",
            )
        except RuntimeError as error:
            if "implicit Scanpy dataset download blocked by TAFFISH" not in str(error):
                raise
        else:
            raise RuntimeError("missing prepared member did not fail before download")

    calls = (
        ("pbmc3k", sc.datasets.pbmc3k),
        (
            "ebi-expression-atlas",
            lambda: sc.datasets.ebi_expression_atlas("TAFFISH-NO-NET"),
        ),
        ("visium-sge", sc.datasets.visium_sge),
    )
    with (
        patch(
            "scanpy.readwrite._download",
            side_effect=RuntimeError("network download path was reached"),
        ),
        patch(
            "scanpy.datasets._ebi_expression_atlas.sniff_url",
            side_effect=RuntimeError("EBI network path was reached"),
        ),
        patch(
            "scanpy.datasets._datasets._download_visium_dataset",
            side_effect=RuntimeError("Visium network path was reached"),
        ),
    ):
        for label, call in calls:
            try:
                call()
            except (FileExistsError, NotADirectoryError):
                continue
            except RuntimeError as error:
                raise RuntimeError(f"{label} did not fail before network access: {error}") from error
            raise RuntimeError(f"{label} did not fail closed without a prepared root")

    original_datasetdir = sc.settings.datasetdir
    try:
        with tempfile.TemporaryDirectory(prefix="taf-scanpy-partial-root-") as temporary:
            sc.settings.datasetdir = Path(temporary)
            partial_calls = (
                ("pbmc3k-partial", sc.datasets.pbmc3k),
                ("paul15-partial", sc.datasets.paul15),
                (
                    "ebi-partial",
                    lambda: sc.datasets.ebi_expression_atlas("TAFFISH-NO-NET"),
                ),
                ("visium-partial", sc.datasets.visium_sge),
            )
            for label, call in partial_calls:
                try:
                    call()
                except RuntimeError as error:
                    if "implicit Scanpy dataset download blocked by TAFFISH" in str(error):
                        continue
                    raise RuntimeError(f"{label} reached an unexpected runtime path: {error}") from error
                raise RuntimeError(f"{label} did not reject a missing member")
    finally:
        sc.settings.datasetdir = original_datasetdir


def check_unverified_dataset_policy() -> None:
    expected_root = Path("/dataset-download")
    if sc.settings.datasetdir != expected_root or not expected_root.is_dir():
        raise RuntimeError("TAFFISH unverified persistent dataset root is not active")

    restricted_calls = (
        ("burczynski06", sc.datasets.burczynski06),
        ("pbmc3k", sc.datasets.pbmc3k),
        ("pbmc3k-processed", sc.datasets.pbmc3k_processed),
        ("moignard15", sc.datasets.moignard15),
        ("paul15", sc.datasets.paul15),
    )

    def require_fixed_members_blocked(suffix: str) -> None:
        for label, call in restricted_calls:
            try:
                call()
            except RuntimeError as error:
                if "implicit Scanpy dataset download blocked by TAFFISH" in str(error):
                    continue
                raise RuntimeError(
                    f"{label}-{suffix} reached an unexpected path: {error}"
                ) from error
            raise RuntimeError(
                f"{label}-{suffix} bypassed the fixed-member resource policy"
            )

    original_datasetdir = sc.settings.datasetdir
    try:
        with tempfile.TemporaryDirectory(
            prefix="taf-scanpy-missing-fixed-", dir=expected_root
        ) as temporary_base:
            missing_datasetdir = Path(temporary_base) / "datasets"
            missing_datasetdir.mkdir()
            sc.settings.datasetdir = missing_datasetdir
            require_fixed_members_blocked("missing")
        with tempfile.TemporaryDirectory(
            prefix="taf-scanpy-existing-fixed-", dir=expected_root
        ) as temporary_base:
            existing_root = Path(temporary_base) / "datasets"
            existing_root.mkdir()
            fixed_paths = (
                Path("burczynski06/GDS1615_full.soft.gz"),
                Path("pbmc3k_raw.h5ad"),
                Path("pbmc3k_processed.h5ad"),
                Path("moignard15/nbt.3154-S3.xlsx"),
                Path("paul15/paul15.h5"),
            )
            for relative_path in fixed_paths:
                fixed_path = existing_root / relative_path
                fixed_path.parent.mkdir(parents=True, exist_ok=True)
                fixed_path.write_bytes(b"taffish-fixed-member-policy-probe\n")
            sc.settings.datasetdir = existing_root
            require_fixed_members_blocked("existing")

        with tempfile.TemporaryDirectory(
            prefix="taf-scanpy-network-probe-", dir=expected_root
        ) as temporary_base:
            network_datasetdir = Path(temporary_base) / "datasets"
            network_datasetdir.mkdir()
            sc.settings.datasetdir = network_datasetdir

            with patch(
                "scanpy.datasets._ebi_expression_atlas.urlopen",
                side_effect=RuntimeError("ebi-network-probe-reached"),
            ):
                try:
                    sc.datasets.ebi_expression_atlas("TAFFISH-NO-NET")
                except RuntimeError as error:
                    if str(error) != "ebi-network-probe-reached":
                        raise
                else:
                    raise RuntimeError(
                        "EBI unverified route did not reach the network probe"
                    )

            with patch(
                "urllib.request.urlopen",
                side_effect=RuntimeError("visium-network-probe-reached"),
            ):
                try:
                    sc.datasets.visium_sge()
                except RuntimeError as error:
                    if str(error) != "visium-network-probe-reached":
                        raise
                else:
                    raise RuntimeError(
                        "Visium unverified route did not reach the network probe"
                    )
    finally:
        sc.settings.datasetdir = original_datasetdir


def main() -> int:
    args = parse_args()
    if args.policy_only:
        check_dataset_policy()
        print("dataset_policy=fail-closed")
        return 0
    if args.unverified_policy_only:
        check_unverified_dataset_policy()
        print("dataset_policy=ebi-visium-only")
        return 0
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    check_regressions()
    check_moignard_excel()
    if args.regressions_only:
        print("regressions=ok")
        return 0

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

    if not args.buildtime:
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
            sc.tl.rank_genes_groups(
                adata,
                groupby="group",
                method="t-test",
                use_raw=True,
            )

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
        ("openpyxl", metadata.version("openpyxl")),
        ("et-xmlfile", metadata.version("et-xmlfile")),
    ]
    pd.DataFrame(versions, columns=["package", "version"]).to_csv(
        outdir / "versions.tsv",
        sep="\t",
        index=False,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
