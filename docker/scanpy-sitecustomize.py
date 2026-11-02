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
    if target == Path("/datasets/scanpy"):
        # Host-side checks are an early diagnostic, not a second trust contract.
        # Use the installer's full catalog/receipt/content validator before analysis.
        helper = runpy.run_path("/opt/scanpy/bin/scanpy-prepare-datasets")
        _, entries = helper["load_catalog"]()
        helper["verify_root"](target, entries, deep=True)

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

    import scanpy._utils as scanpy_utils
    import scanpy.datasets._ebi_expression_atlas as ebi_atlas
    import scanpy.readwrite as scanpy_readwrite

    original_download = scanpy_readwrite._download
    original_datafile_check = scanpy_readwrite._check_datafile_present_and_download

    if unverified_mode:
        def controlled_download(url, path):
            if not str(url).startswith(VISIUM_URL_PREFIX):
                blocked_download(url, path)
            return original_download(url, path)

        def controlled_datafile_check(path, backup_url=None):
            if backup_url is not None and not str(backup_url).startswith(
                VISIUM_URL_PREFIX
            ):
                blocked_download(backup_url, path)
            return original_datafile_check(path, backup_url=backup_url)

        def controlled_presence_download(filename, backup_url):
            if not str(backup_url).startswith(VISIUM_URL_PREFIX):
                blocked_download(backup_url, filename)
            if not filename.is_file():
                controlled_download(backup_url, filename)

        scanpy_readwrite._download = controlled_download
        scanpy_readwrite._check_datafile_present_and_download = controlled_datafile_check
        scanpy_utils.check_presence_download = controlled_presence_download
    else:
        def offline_presence_download(filename, backup_url):
            path = Path(filename)
            if path.is_file() and not path.is_symlink():
                return
            blocked_download(backup_url, filename)

        scanpy_readwrite._download = blocked_download
        scanpy_utils.check_presence_download = offline_presence_download
        ebi_atlas._download = blocked_download
        ebi_atlas.sniff_url = blocked_download


try:
    apply_policy()
except Exception as error:  # sitecustomize exceptions are otherwise non-fatal
    sys.stderr.write(f"taf-scanpy: dataset policy initialization failed: {error}\n")
    sys.stderr.flush()
    os._exit(125)
