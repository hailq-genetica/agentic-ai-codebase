"""
Tool registry for scselected scATAC-seq tools.

Curated subset of single-cell ATAC tools using SnapATAC2.
Category: scselected_scatac
Implementation: src.tool_scselected.scatac
"""

description = [
    {
        "name": "scATAC_calculate_qc_metrics",
        "description": "Calculate QC metrics for scATAC-seq data using SnapATAC2. Computes fragment size distribution, nucleosome signal, and TSS enrichment (hg38). Returns violin plots of n_fragments, TSS enrichment, and nucleosome signal.",
        "required_parameters": [],
        "optional_parameters": [],
        "is_plotting": True,
    },
    {
        "name": "scATAC_qc_filter_cells",
        "description": "Filter cells based on QC metrics. Uses min_counts, max_counts, min_tsse for snap.pp.filter_cells, and max_nucleosome_signal for additional filtering. Should be called after scATAC_calculate_qc_metrics.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "min_counts",
                "type": "int",
                "description": "Minimum total counts per cell.",
                "default": None
            },
            {
                "name": "min_tsse",
                "type": "float",
                "description": "Minimum TSS enrichment score per cell.",
                "default": None
            },
            {
                "name": "max_counts",
                "type": "int",
                "description": "Maximum total counts per cell.",
                "default": None
            },
            {
                "name": "max_nucleosome_signal",
                "type": "float",
                "description": "Maximum nucleosome signal. Cells above are removed (poor fragmentation).",
                "default": None
            },
        ],
    },
    {
        "name": "scATAC_calculate_tiles",
        "description": "Add tile matrix to the AnnData object using snap.pp.add_tile_matrix. This step adds n_vars (genomic bins) and is required before feature selection.",
        "required_parameters": [],
        "optional_parameters": [],
    },
    {
        "name": "scATAC_feature_selection",
        "description": "Select top features (genomic bins) by variability using snap.pp.select_features. Should be called after scATAC_calculate_tiles.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_features",
                "type": "int",
                "description": "Number of top features to select.",
                "default": 250000
            },
        ],
    },
    {
        "name": "scATAC_doublet_detection",
        "description": "Detect doublets using Scrublet via snap.pp.scrublet. Adds doublet_probability to adata.obs and generates a histogram of doublet probabilities. Does NOT remove doublets.",
        "required_parameters": [],
        "optional_parameters": [],
        "is_plotting": True,
    },
    {
        "name": "scATAC_filter_doublets",
        "description": "Remove detected doublets based on a probability threshold. Should be called after scATAC_doublet_detection.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "threshold",
                "type": "float",
                "description": "Doublet probability threshold. Cells above are removed.",
                "default": 0.5
            },
        ],
    },
    {
        "name": "scATAC_dimensionality_reduction",
        "description": "Perform spectral embedding dimensionality reduction using snap.tl.spectral. Returns eigenvalue elbow plot and cumulative proportion plot.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_comps",
                "type": "int",
                "description": "Number of spectral components to compute.",
                "default": 100
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scATAC_batch_correction",
        "description": "Perform batch correction using Harmony or Scanorama via SnapATAC2. Requires spectral embedding to be computed first via scATAC_dimensionality_reduction.",
        "required_parameters": [
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches."
            },
        ],
        "optional_parameters": [
            {
                "name": "method",
                "type": "str",
                "description": "Batch correction method: 'harmony' or 'scanorama'.",
                "default": "harmony"
            },
        ],
    },
    {
        "name": "scATAC_clustering",
        "description": "Perform KNN graph construction, Leiden clustering, and UMAP on scATAC data using spectral embeddings. Returns UMAP plot colored by leiden cluster.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_comps",
                "type": "int",
                "description": "Number of UMAP components.",
                "default": 2
            },
            {
                "name": "n_neighbors",
                "type": "int",
                "description": "Number of neighbors for KNN graph.",
                "default": 50
            },
            {
                "name": "resolution",
                "type": "float",
                "description": "Resolution parameter for Leiden clustering (higher = more clusters).",
                "default": 0.5
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scATAC_identify_marker_peaks",
        "description": "Identify marker peaks per cell type using MACS3 peak calling and motif enrichment via SnapATAC2. Calls peaks, merges them, finds marker regions, and performs motif enrichment. Saves results (peaks, marker_peaks, motifs) as CSV files to output_dir.",
        "required_parameters": [
            {
                "name": "cell_type_key",
                "type": "str",
                "description": "Column in adata.obs containing cell type annotations for grouping."
            },
        ],
        "optional_parameters": [
            {
                "name": "output_dir",
                "type": "str",
                "description": "Directory to save output CSV files (marker_peaks.csv, peak_mat.csv, motifs.csv).",
                "default": "."
            },
        ],
        "is_plotting": True,
    },
]
