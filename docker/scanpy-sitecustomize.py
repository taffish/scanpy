"""Apply the TAFFISH Scanpy dataset policy before user code imports Scanpy."""

from __future__ import annotations

import os
from pathlib import Path
import runpy
import sys


POLICY = "managed-v1"
DISABLED_SENTINEL = Path(
    "/opt/scanpy/share/scanpy/TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED"
)
ALLOWED_DATASETDIRS = {
    DISABLED_SENTINEL,
    Path("/datasets/scanpy"),
    Path("/dataset-download"),
}
VISIUM_URL_PREFIX = "https://exampledata.scverse.org/scanpy/visium/"


def is_container_mount(path: Path) -> bool:
    try:
        for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) > 4 and fields[4] == str(path):
                return True
    except OSError:
        return False
    return False


def apply_policy() -> None:
    if os.environ.get("TAFFISH_SCANPY_DATASET_POLICY", POLICY) != POLICY:
        raise RuntimeError("TAFFISH Scanpy dataset policy identity is invalid")
    configured = os.environ.get(
        "TAFFISH_SCANPY_DATASETDIR", str(DISABLED_SENTINEL)
    )
    target = Path(configured)
    if target not in ALLOWED_DATASETDIRS:
        raise RuntimeError(f"TAFFISH Scanpy dataset directory is not allowed: {target}")
    if target == DISABLED_SENTINEL:
        if not target.is_file() or target.is_symlink():
            raise RuntimeError("TAFFISH Scanpy download-disable sentinel is missing")
    elif not target.is_dir() or not is_container_mount(target):
        raise RuntimeError(
            f"TAFFISH Scanpy dataset directory is not a persistent container mount: {target}"
        )
    installed = {}
    if target == Path("/datasets/scanpy"):
        # Host-side checks are an early diagnostic, not a second trust contract.
        # Use the installer's full catalog/receipt/content validator before analysis.
        helper = runpy.run_path("/opt/scanpy/bin/scanpy-prepare-datasets")
        _, entries = helper["load_catalog"]()
        records = helper["verify_root"](target, entries, deep=True)
        installed = {r["dataset_id"]: entries[r["dataset_id"]] for r in records}

    allow_network = os.environ.get("TAFFISH_SCANPY_ALLOW_NETWORK", "0")
    allow_unverified = os.environ.get(
        "TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS", "0"
    )
    if allow_network not in {"0", "1"} or allow_unverified not in {"0", "1"}:
        raise RuntimeError("TAFFISH Scanpy network policy flags accept only 0 or 1")
    unverified_mode = (
        target == Path("/dataset-download")
        and allow_network == "1"
        and allow_unverified == "1"
    )
    if target == Path("/dataset-download") and not unverified_mode:
        raise RuntimeError(
            "the unverified download root requires both explicit network opt-ins"
        )
    if target != Path("/dataset-download") and allow_unverified == "1":
        raise RuntimeError(
            "unverified-download opt-in requires the persistent /dataset-download mount"
        )

    import scanpy as sc

    sc.settings.datasetdir = target
    if sc.settings.datasetdir != target.resolve():
        raise RuntimeError("Scanpy rejected the TAFFISH dataset directory policy")
    def blocked_download(*_args, **_kwargs):
        raise RuntimeError(
            "implicit Scanpy dataset download blocked by TAFFISH; "
            "prepare a fixed member or use the explicit persistent EBI/Visium opt-in"
        )

    import functools
    import re
    import scanpy.datasets._datasets as dataset_api
    import scanpy.datasets._utils as registry
    import scanpy.datasets._ebi_expression_atlas as ebi_atlas
    import scanpy.io._download as download_api
    import scanpy.io._read as read_api
    import scanpy.readwrite as legacy_io

    # The scientific readers remain upstream. Resolve the five registry entries
    # to verified files without letting pooch create locks or caches on a site mount.
    def fixed_member(name):
        dataset_id = {"pbmc3k": "pbmc3k-raw", "pbmc3k_processed": "pbmc3k-processed"}.get(name, name)
        if sc.settings.datasetdir != target or dataset_id not in installed:
            return blocked_download(name)
        entry = installed[dataset_id]
        helper["verify_member"](target, entry, deep=True)
        return target / entry.relative_path

    registry.fetch_dataset = dataset_api.fetch_dataset = fixed_member
    upstream_download = download_api.download

    def allowed_root():
        current = sc.settings.datasetdir
        if not unverified_mode or not current.is_relative_to(target) or current.resolve() != current:
            blocked_download(current)
        return current

    def online_reader(reader, argument, default=None):
        @functools.wraps(reader)
        def wrapped(*args, **kwargs):
            root = allowed_root()
            identifier = args[0] if args else kwargs.get(argument, default)
            if not isinstance(identifier, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", identifier):
                raise ValueError(f"expected a single {argument} identifier")
            directory = root / identifier
            if directory.is_symlink() or (directory.is_dir() and any(p.is_symlink() for p in directory.rglob("*"))):
                raise ValueError("unexpected symbolic link in the dataset cache")
            return reader(*args, **kwargs)
        return wrapped

    def online_download(url, path):
        root = allowed_root()
        path = Path(path)
        if not path.is_relative_to(root) or path.resolve() != path:
            blocked_download(url, path)
        if not (url.startswith(VISIUM_URL_PREFIX) or url.startswith("https://www.ebi.ac.uk/gxa/sc/experiment/")):
            blocked_download(url, path)
        return upstream_download(url, path)

    # The generic backup_url API is not a third, undocumented network opt-in.
    def local_only(url, path):
        if Path(path).is_file() and not Path(path).is_symlink():
            return
        blocked_download(url, path)

    read_api.download = legacy_io.download = download_api.download = local_only
    dataset_api.download = ebi_atlas.download = online_download
    query = online_reader(ebi_atlas.ebi_expression_atlas, "accession")
    visium = online_reader(dataset_api.visium_sge, "sample_id", "V1_Breast_Cancer_Block_A_Section_1")
    sc.datasets.ebi_expression_atlas = ebi_atlas.ebi_expression_atlas = query
    sc.datasets.visium_sge = dataset_api.visium_sge = visium
    if not unverified_mode:
        ebi_atlas.sniff_url = blocked_download


try:
    apply_policy()
except Exception as error:  # sitecustomize exceptions are otherwise non-fatal
    sys.stderr.write(f"taf-scanpy: dataset policy initialization failed: {error}\n")
    sys.stderr.flush()
    os._exit(125)
