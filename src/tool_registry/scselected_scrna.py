"""
Tool registry for scselected scRNA-seq tools.

Curated subset of single-cell RNA tools for common workflows.
Category: scselected_scrna
Implementation: src.tool_scselected.scrna
"""

description = [
    {
        "name": "scRNA_calculate_qc_metrics",
        "description": "Calculate quality control metrics for single-cell data including mitochondrial, ribosomal, and hemoglobin gene percentages. Returns the AnnData with QC metrics and violin/scatter plots. If batch_key is provided, generates per-batch QC plots.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "qc_vars",
                "type": "list",
                "description": "Keys for QC variables to calculate (e.g., ['mt', 'ribo', 'hb'])",
                "default": ["mt", "ribo", "hb"]
            },
            {
                "name": "layer",
                "type": "str",
                "description": "If provided, use adata.layers[layer] for expression values",
                "default": None
            },
            {
                "name": "use_raw",
                "type": "bool",
                "description": "If True, use adata.raw.X for expression values",
                "default": False
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches. If provided, computes QC per batch with per-batch plots.",
                "default": None
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_perform_qc_filtering",
        "description": "Filter cells and genes based on QC metrics. Removes cells with too few genes and genes expressed in too few cells. If batch_key is provided, reports per-batch filtering statistics.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "min_genes",
                "type": "int",
                "description": "Minimum number of genes per cell",
                "default": 200
            },
            {
                "name": "min_cells",
                "type": "int",
                "description": "Minimum number of cells per gene",
                "default": 3
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches. If provided, reports per-batch filtering statistics.",
                "default": None
            },
        ],
    },
    {
        "name": "scRNA_remove_high_mt_cells",
        "description": "Remove cells with a high percentage of mitochondrial reads. Should be called after scRNA_calculate_qc_metrics.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "max_mt_pct",
                "type": "float",
                "description": "Maximum mitochondrial percentage threshold. Cells above this are removed.",
                "default": 20.0
            },
        ],
    },
    {
        "name": "scRNA_get_doublet_scores",
        "description": "Compute doublet scores using Scrublet. Does NOT remove doublets - only calculates scores and shows distribution plot. After inspecting the plot, filter manually: adata = adata[adata.obs['doublet_score'] < threshold]",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches for batch-aware doublet detection. If None, runs on entire dataset.",
                "default": None
            },
            {
                "name": "threshold",
                "type": "float",
                "description": "Threshold for reporting statistics only. Does NOT filter cells. Typical values: 0.2-0.4.",
                "default": 0.3
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_normalize_data",
        "description": "Normalize data using size factors and log1p transformation. Stores raw counts in layers['counts'] and normalized data in layers['log1p_norm']. If batch_key is provided, normalizes each batch independently.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "target_sum",
                "type": "float",
                "description": "Target sum for size factor normalization. If None, uses median count depth.",
                "default": 10000
            },
            {
                "name": "default_layer",
                "type": "str",
                "description": "Which normalization to use as adata.X ('log1p_norm')",
                "default": "log1p_norm"
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches. If provided, normalizes each batch independently.",
                "default": None
            },
        ],
    },
    {
        "name": "scRNA_feature_selection",
        "description": "Identify highly variable genes for downstream analysis. Saves full data in adata.raw and subsets to HVGs. If batch_key is provided, uses batch-aware HVG selection.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_top_genes",
                "type": "int",
                "description": "Number of top highly variable genes to select",
                "default": 2000
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches. If provided, uses batch-aware HVG selection.",
                "default": None
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_dimensionality_reduction",
        "description": "Perform scaling and PCA dimensionality reduction. Returns variance ratio plot.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_components",
                "type": "int",
                "description": "Number of principal components to compute",
                "default": 100
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches (for reference, does not affect PCA computation).",
                "default": None
            },
            {
                "name": "random_state",
                "type": "int",
                "description": "Random seed for reproducibility",
                "default": 42
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_batch_correction",
        "description": "Perform batch correction on PCA embeddings using Harmony or Scanorama. Requires PCA to be computed first via scRNA_dimensionality_reduction.",
        "required_parameters": [
            {
                "name": "batch_keys",
                "type": "list",
                "description": "List of column names in adata.obs to use for batch correction. For Scanorama, only one key is supported."
            },
        ],
        "optional_parameters": [
            {
                "name": "method",
                "type": "str",
                "description": "Batch correction method: 'harmony' or 'scanorama'",
                "default": "harmony"
            },
            {
                "name": "random_state",
                "type": "int",
                "description": "Random seed for reproducibility",
                "default": 42
            },
        ],
    },
    {
        "name": "scRNA_clustering",
        "description": "Perform neighborhood graph construction, Leiden clustering, and UMAP on the AnnData object. Returns UMAP plot colored by cluster and optionally by batch.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "n_pcs",
                "type": "int",
                "description": "Number of PCs to use for neighbor graph",
                "default": 30
            },
            {
                "name": "n_neighbors",
                "type": "int",
                "description": "Number of neighbors for kNN graph",
                "default": 15
            },
            {
                "name": "resolution",
                "type": "float",
                "description": "Resolution parameter for Leiden clustering (higher = more clusters)",
                "default": 0.5
            },
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs identifying batches. If provided, shows batch in UMAP.",
                "default": None
            },
            {
                "name": "random_state",
                "type": "int",
                "description": "Random seed for reproducibility",
                "default": 42
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_cnmf_factorization",
        "description": "Run consensus NMF (cNMF) per cell type to identify gene expression programs. Assumes adata is already subset to HVGs and has raw counts in layers['counts']. Auto-selects K based on highest stability.",
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": "cell_type_key",
                "type": "str",
                "description": "Column in adata.obs containing cell type annotations",
                "default": "leiden"
            },
            {
                "name": "output_dir",
                "type": "str",
                "description": "Directory to write cNMF output files",
                "default": "./cnmf_results"
            },
            {
                "name": "components",
                "type": "list",
                "description": "K values (number of programs) to test",
                "default": [5, 10, 15, 20]
            },
            {
                "name": "n_iter",
                "type": "int",
                "description": "Number of NMF iterations per K",
                "default": 100
            },
            {
                "name": "density_threshold",
                "type": "float",
                "description": "Local density threshold for consensus clustering",
                "default": 0.1
            },
            {
                "name": "seed",
                "type": "int",
                "description": "Random seed for reproducibility",
                "default": 42
            },
        ],
        "is_plotting": True,
    },
    {
        "name": "scRNA_infercnv",
        "description": "Run inferCNV to identify tumor vs normal cells based on copy number variation profiles. Requires cell type annotations.",
        "required_parameters": [
            {
                "name": "cell_type_key",
                "type": "str",
                "description": "Column in adata.obs containing cell type annotations"
            },
            {
                "name": "reference_cat",
                "type": "list",
                "description": "Cell types to use as reference 'normal' cells (e.g., immune cells)"
            },
            {
                "name": "tumor_cell_types",
                "type": "list",
                "description": "Cell types to classify as tumor (e.g., ['Epithelial cell'])"
            },
        ],
        "optional_parameters": [
            {
                "name": "batch_key",
                "type": "str",
                "description": "Column in adata.obs for batch. If provided, generates per-batch plots.",
                "default": None
            },
            {
                "name": "window_size",
                "type": "int",
                "description": "Window size for smoothing",
                "default": 250
            },
        ],
        "is_plotting": True,
    },
]
