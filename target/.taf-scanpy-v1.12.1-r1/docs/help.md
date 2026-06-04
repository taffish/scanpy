scanpy 1.12.1-r1

Purpose:
  Python 3.12 Scanpy runtime and upstream Scanpy CLI for single-cell
  gene-expression analysis with AnnData, preprocessing, clustering, marker
  testing, and plotting support.

Usage:
  taf-scanpy --help
  taf-scanpy --version
  taf-scanpy -- --help
  taf-scanpy scanpy --help
  taf-scanpy python analysis.py
  taf-scanpy python -c '"import importlib.metadata as md; print(md.version(\"scanpy\"))"'

Wrapper options:
  -h, --help       Show this TAFFISH help.
  -v, --version    Show the TAFFISH package version.
  --compile        Print generated shell code instead of running it.
  --               Pass following option-leading arguments to the default
                   upstream command, scanpy.

Default upstream command:
  scanpy

Command mode:
  This app keeps TAFFISH command mode enabled. Non-option-leading arguments run
  commands inside the same Scanpy container.

  Examples:
    taf-scanpy python script.py
    taf-scanpy python -c '"import importlib.metadata as md; print(md.version(\"scanpy\"))"'
    taf-scanpy scanpy --help
    taf-scanpy pip list

  For python -c, keep the code string quoted as a literal argument as shown
  above. For multi-line analysis, use a script file or stdin.

Common input files:
  .h5ad, 10x Matrix Market directories, 10x HDF5, .loom, .mtx, .csv, .tsv, and
  other files supported by Scanpy and AnnData readers.

Common output files:
  Processed .h5ad objects, marker tables, QC or clustering tables, and static
  figures written by Scanpy or matplotlib. Your Python script controls all
  output paths.

Packaged Python stack:
  Python 3.12, Scanpy 1.12.1, AnnData, NumPy, SciPy, pandas, h5py,
  scikit-learn, matplotlib, seaborn, statsmodels, UMAP, pynndescent, numba,
  networkx, igraph, leidenalg, and scikit-misc.

Included optional Scanpy extras:
  leiden    Enables Scanpy Leiden clustering.
  skmisc    Enables highly_variable_genes(..., flavor="seurat_v3").

Platform:
  Native linux/amd64 and linux/arm64 builds are intended. No GPU runtime
  arguments are configured in r1.

Boundaries:
  r1 is an offline runtime. It does not bundle large reference atlases, model
  weights, JupyterLab, bbknn, harmonypy, magic-impute, scanorama, scrublet,
  Dask acceleration, RAPIDS/GPU packages, legacy louvain, or online
  data-download workflows. Louvain is not bundled in r1 because its PyPI package
  currently requires source-build tooling on Python 3.12; use Leiden for the
  packaged clustering path.

Citation:
  Wolf, Angerer, and Theis. SCANPY: large-scale single-cell gene expression
  data analysis. Genome Biology 19, 15 (2018). doi:
  10.1186/s13059-017-1382-0; PMID: 29409532.
