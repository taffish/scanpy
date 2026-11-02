scanpy 1.12.5-r1

Purpose:
  Run CPU/headless Scanpy Python analysis on local single-cell data.
  Analysis uses the Python API; the upstream CLI mainly exposes settings.

Common tasks:
  taf-scanpy python analysis.py input.h5ad output.h5ad
  taf-scanpy scanpy settings
  taf-scanpy -- --help
  Use script files for multiline Python. Automatic command mode needs literal
  quotes around arguments with spaces, not just shell grouping:
  taf-scanpy python analysis.py "'input with spaces.h5ad'" "'output with spaces.h5ad'"

Inputs and outputs:
  Supply a Python script and local H5AD/10x/Matrix Market data as it requires.
  Scripts choose output H5AD, TSV/CSV and static PNG/SVG/PDF paths.
  Existing output handling belongs to the script; choose a new output directory.

Dataset safety:
  Implicit Scanpy example downloads fail before network access by default.
  Docker/Podman additionally disable networking. Prepared roots are read-only;
  Scanpy settings.datasetdir is configured automatically on all three backends.

Prepare one fixed dataset:
  taf-scanpy scanpy-prepare-datasets --list-datasets
  taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw --dry-run
  ROOT="$HOME/.local/share/taffish/datasets/scanpy"; mkdir -p "$ROOT"
  Docker: TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_ALLOW_NETWORK=1 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
  Podman: TAFFISH_CONTAINER_BACKEND=podman TAFFISH_SCANPY_ALLOW_NETWORK=1 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
  Apptainer: TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_SCANPY_ALLOW_NETWORK=1 \
    TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets --dataset pbmc3k-raw
  Automatic members: burczynski06, pbmc3k-raw, pbmc3k-processed. Select only one.
  moignard15/paul15 need an independently authorized file under "$ROOT/imports":
  TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" taf-scanpy scanpy-prepare-datasets \
    --dataset moignard15 --source-file /dataset-install/imports/nbt.3154-S3.xlsx \
    --confirm-authorized-local-import

Find and share resources:
  The helper creates "$ROOT/1.12.5". Personal discovery uses
  ~/.local/share/taffish/datasets/scanpy/1.12.5; site discovery uses
  /usr/local/share/taffish/datasets/scanpy/1.12.5, then /opt/taffish/datasets/scanpy/1.12.5.
  An administrator can prepare once and grant read/traverse access to all users;
  no ordinary-user download is needed. Full setup and permissions: README.
  Host resource paths cannot contain whitespace, commas, colons or * ? [ ].
  Explicit override (same command on all backends):
  TAFFISH_CONTAINER_BACKEND=docker TAFFISH_SCANPY_DATASET_PATH=/host/version/root taf-scanpy python analysis.py
  TAFFISH_CONTAINER_BACKEND=podman TAFFISH_SCANPY_DATASET_PATH=/host/version/root taf-scanpy python analysis.py
  TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_SCANPY_DATASET_PATH=/host/version/root taf-scanpy python analysis.py
  TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 disables discovery and explicit root use.
  Missing/corrupt roots fail; they never silently trigger a replacement download.
  FileExistsError mentioning TAFFISH_IMPLICIT_DATASET_DOWNLOADS_DISABLED means
  that no prepared root is selected: prepare/select a resource before that call.

Verify or recover:
  TAFFISH_SCANPY_DATASET_AUTO_MOUNT=0 TAFFISH_SCANPY_DATASET_INSTALL_ROOT="$ROOT" \
    taf-scanpy scanpy-prepare-datasets --verify-only --dataset-root /dataset-install/1.12.5
  Keep any reported recovery directory. Review the source, then add --force to
  the same exact-member install command; disable auto-mount while repairing.
  Never remove another member or an old recovery directory to bypass a failure.

Explicit evolving online input:
  Only EBI accessions or legacy Visium: prefer a frozen local input instead.
  ONLINE_ROOT="$PWD/scanpy-unverified-downloads"; mkdir -p "$ONLINE_ROOT"
  unset TAFFISH_SCANPY_DATASET_PATH TAFFISH_SCANPY_DATASET_INSTALL_ROOT
  export TAFFISH_SCANPY_ALLOW_NETWORK=1 TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS=1
  export TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT="$ONLINE_ROOT"
  TAFFISH_CONTAINER_BACKEND=docker taf-scanpy python online.py
  TAFFISH_CONTAINER_BACKEND=podman taf-scanpy python online.py
  TAFFISH_CONTAINER_BACKEND=apptainer taf-scanpy python online.py
  unset TAFFISH_SCANPY_ALLOW_NETWORK TAFFISH_SCANPY_ALLOW_UNVERIFIED_DOWNLOADS
  unset TAFFISH_SCANPY_UNVERIFIED_DOWNLOAD_ROOT
  No fixed checksum or uniform license: authorize and freeze results before reuse.

Immediate limits:
  Wheel-bundled examples need no helper. Query clients/loompy are not included.
  GPU is unsupported on all backends: RAPIDS/CUDA is absent; flags cannot add it.
  No Jupyter/Cell Browser service or port is included; export H5AD for a viewer.
  The Scanpy download policy is not an Apptainer-wide network firewall.
  Docker normally writes as root; site admins handle ownership/repair as in README.

More help:
  https://github.com/taffish/scanpy
  https://scanpy.scverse.org/
  taf-scanpy --help       Show this help.
  taf-scanpy --version    Show the TAFFISH package version.
  taf-scanpy --compile    Print generated wrapper shell code.
