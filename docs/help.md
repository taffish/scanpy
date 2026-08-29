scanpy 1.12.4-r1

Purpose:
  Run CPU/headless Scanpy Python analyses on local single-cell data. Use Python
  for analysis; the upstream scanpy CLI mainly exposes settings.

Common tasks:
  taf-scanpy python analysis.py input.h5ad output.h5ad
  taf-scanpy scanpy settings
  taf-scanpy -- --help

Default dataset safety:
  Docker/Podman wrapper runs are network-disabled by default. On every backend,
  implicit Scanpy example downloads fail closed before network access. A valid
  prepared root is mounted read-only and becomes sc.settings.datasetdir
  automatically; scripts do not need to bind it themselves.

Prepare a fixed example dataset:
  taf-scanpy scanpy-prepare-datasets --list-datasets
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run
  ROOT="$HOME/.local/share/taffish/datasets/scanpy"; mkdir -p "$ROOT"
  Docker: TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_ALLOW_NETWORK=1 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
  Podman: TAFFISH_CONTAINER_BACKEND=podman TAFFISH_SCANPY_ALLOW_NETWORK=1 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
  Apptainer: same variables/backend=apptainer; contract-only here—use Docker/Podman.

  Automatic fixed members: burczynski06, pbmc3k-raw, pbmc3k-processed.
  moignard15 and paul15 require an independently authorized exact local file:
  TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets \
    --dataset moignard15 --source-file /dataset-install/imports/nbt.3154-S3.xlsx \
    --confirm-authorized-local-import
  Verify/repair with TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy \
    scanpy-prepare-datasets --verify-only --dataset-root /dataset-install/1.12.4

Install and reuse paths:
  The writable host parent appears as /dataset-install; the helper creates the
  1.12.4 root atomically. Personal discovery uses:
    ~/.local/share/taffish/datasets/scanpy/1.12.4
  Site discovery uses /usr/local/share/.../scanpy/1.12.4, then /opt/... .
  An administrator may prepare once, verify, set root:root and a+rX, then all
  users reuse it read-only. Docker output is normally root-owned; admin handles
  repair/removal. Rootless Podman/Apptainer normally retain caller ownership.

Use a prepared root on each backend:
  TAFFISH_SCANPY_DATASET_PATH=/host/version/root \
    TAFFISH_CONTAINER_BACKEND=docker taf-scanpy python analysis.py
  TAFFISH_SCANPY_DATASET_PATH=/host/version/root \
    TAFFISH_CONTAINER_BACKEND=podman taf-scanpy python analysis.py
  TAFFISH_SCANPY_DATASET_PATH=/host/version/root \
    TAFFISH_CONTAINER_BACKEND=apptainer taf-scanpy python analysis.py
  Apptainer prepared-root use is likewise compile/contract-only on this host.
  Disable discovery with TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0. Missing, partial,
  modified or symlink-containing prepared roots fail before container start.

Explicit evolving online input (unverified and nonreproducible):
  ONLINE_ROOT="$PWD/scanpy-unverified-downloads"; mkdir -p "$ONLINE_ROOT"
  unset TAFFISH_SCANPY_DATASET_PATH TAFFISH_SCANPY_DATASET_INSTALL_ROOT
  export TAFFISH_SCANPY_ALLOW_NETWORK=1
  export TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS=1
  export TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT="$ONLINE_ROOT"
  TAFFISH_CONTAINER_BACKEND=docker taf-scanpy python online.py
  TAFFISH_CONTAINER_BACKEND=podman taf-scanpy python online.py
  TAFFISH_CONTAINER_BACKEND=apptainer taf-scanpy python online.py
  unset TAFFISH_SCANPY_ALLOW_NETWORK TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS
  unset TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT

  This route is only for EBI accessions or legacy Visium examples that cannot
  use a frozen local input. It has no app-fixed checksum/member inventory or
  uniform license; freeze and authorize results before reuse. Do not combine it
  with TAFFISH_SCANPY_DATASET_PATH or TAFFISH_SCANPY_DATASET_INSTALL_ROOT.
  Apptainer online use is also compile/contract-only; no runtime is installed.

Immediate resource limits:
  krumsiek11, toggleswitch and pbmc68k_reduced are wheel-built; no helper needed.
  Prefer authorized local Visium data or a reviewed Squidpy app. EBI responses
  evolve. scanpy.queries is unavailable because its clients are not installed.

Backend-sensitive limits:
  GPU is unsupported on Docker/Podman/Apptainer; RAPIDS-singlecell/CUDA is absent.
  Browser/notebook is N/A; no Jupyter or Cell Browser service/port is included.
  Apptainer's Python policy blocks Scanpy downloads, but is not a general network
  firewall; use site isolation when other Python clients must also be offline.

Wrapper options:
  taf-scanpy --help       Show this installed-wrapper help.
  taf-scanpy --version    Show the TAFFISH package version.
  taf-scanpy --compile    Print generated wrapper shell code.
  taf-scanpy -- --help    Pass --help to the upstream scanpy command.
