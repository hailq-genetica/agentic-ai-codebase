"""
Tool definitions for muon ATAC-seq and multimodal single-cell analysis functions.
Format follows Biomni tool description convention.

AUTO-GENERATED from tools_singlecell/atac.py - Regenerate with generate_tool_registry.py
"""

description = [
    # =============================================================================
    # MULTIMODAL I/O FUNCTIONS
    # =============================================================================
    {
        "name": 'scMulti_read_10x_h5',
        "description": 'Read 10x Genomics multimodal HDF5 file (e.g., Multiome ATAC+GEX). Returns MuData with rna and atac modalities.',
        "required_parameters": [
            {
                "name": 'filename',
                "type": 'str',
                "description": 'Path to HDF5 file (e.g., filtered_feature_bc_matrix.h5).',
                "default": None
            },
        ],
        "optional_parameters": [
            {
                "name": 'extended',
                "type": 'bool',
                "description": 'If True, return MuData with separate modalities.',
                "default": True
            },
            {
                "name": 'genome',
                "type": 'str or None',
                "description": 'Genome name filter.',
                "default": None
            },
            {
                "name": 'gex_only',
                "type": 'bool',
                "description": 'If True, only return gene expression data.',
                "default": False
            },
        ],
    },
    {
        "name": 'scMulti_read_10x_mtx',
        "description": 'Read 10x Genomics multimodal MTX directory.',
        "required_parameters": [
            {
                "name": 'path',
                "type": 'str',
                "description": 'Path to directory containing matrix.mtx, features.tsv, barcodes.tsv.',
                "default": None
            },
        ],
        "optional_parameters": [
            {
                "name": 'var_names',
                "type": 'str',
                "description": "Variable names ('gene_symbols' or 'gene_ids').",
                "default": 'gene_symbols'
            },
            {
                "name": 'make_unique',
                "type": 'bool',
                "description": 'Make variable names unique.',
                "default": True
            },
            {
                "name": 'gex_only',
                "type": 'bool',
                "description": 'If True, only return gene expression data.',
                "default": False
            },
        ],
    },
    {
        "name": 'scMulti_read_h5mu',
        "description": 'Read MuData from H5MU file.',
        "required_parameters": [
            {
                "name": 'filename',
                "type": 'str',
                "description": 'Path to H5MU file.',
                "default": None
            },
        ],
        "optional_parameters": [
            {
                "name": 'backed',
                "type": 'str or None',
                "description": "Backed mode ('r' or 'r+').",
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_write_h5mu',
        "description": 'Write MuData to H5MU file.',
        "required_parameters": [
            {
                "name": 'filename',
                "type": 'str',
                "description": 'Path for output file.',
                "default": None
            },
        ],
        "optional_parameters": [
            {
                "name": 'compression',
                "type": 'str or None',
                "description": "Compression ('gzip', 'lzf', or None).",
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_create_from_anndata',
        "description": 'Create MuData from dictionary of AnnData objects. E.g., {"rna": adata_rna, "atac": adata_atac}',
        "required_parameters": [
            {
                "name": 'data_dict',
                "type": 'dict',
                "description": 'Dictionary mapping modality names to AnnData objects.',
                "default": None
            },
        ],
        "optional_parameters": [],
    },
    # =============================================================================
    # ATAC PREPROCESSING FUNCTIONS
    # =============================================================================
    {
        "name": 'scATAC_pp_tfidf',
        "description": 'TF-IDF (Term Frequency-Inverse Document Frequency) normalization for ATAC data. This is the standard normalization for ATAC-seq, analogous to normalize_total + log1p for RNA-seq.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'log_tf',
                "type": 'bool',
                "description": 'Apply log to term frequency.',
                "default": True
            },
            {
                "name": 'log_idf',
                "type": 'bool',
                "description": 'Apply log to inverse document frequency.',
                "default": True
            },
            {
                "name": 'log_tfidf',
                "type": 'bool',
                "description": 'Apply log to TF-IDF product.',
                "default": False
            },
            {
                "name": 'scale_factor',
                "type": 'float',
                "description": 'Scale factor for TF.',
                "default": 10000.0
            },
            {
                "name": 'inplace',
                "type": 'bool',
                "description": 'Modify in place.',
                "default": True
            },
        ],
    },
    {
        "name": 'scATAC_pp_binarize',
        "description": 'Binarize the count matrix (convert to 0/1).',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'threshold',
                "type": 'float',
                "description": 'Values above threshold become 1, rest become 0.',
                "default": 0
            },
            {
                "name": 'copy',
                "type": 'bool',
                "description": 'Return a copy.',
                "default": False
            },
        ],
    },
    {
        "name": 'scATAC_pp_filter_peaks',
        "description": 'Filter peaks (features) based on number of cells or counts.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'min_cells',
                "type": 'int or None',
                "description": 'Minimum number of cells with peak accessible.',
                "default": None
            },
            {
                "name": 'min_counts',
                "type": 'int or None',
                "description": 'Minimum total counts for a peak.',
                "default": None
            },
            {
                "name": 'max_cells',
                "type": 'int or None',
                "description": 'Maximum number of cells with peak accessible.',
                "default": None
            },
            {
                "name": 'max_counts',
                "type": 'int or None',
                "description": 'Maximum total counts for a peak.',
                "default": None
            },
            {
                "name": 'inplace',
                "type": 'bool',
                "description": 'Modify in place.',
                "default": True
            },
        ],
    },
    {
        "name": 'scATAC_pp_filter_cells',
        "description": 'Filter cells based on number of peaks or counts.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'min_peaks',
                "type": 'int or None',
                "description": 'Minimum number of peaks accessible in a cell.',
                "default": None
            },
            {
                "name": 'min_counts',
                "type": 'int or None',
                "description": 'Minimum total counts for a cell.',
                "default": None
            },
            {
                "name": 'max_peaks',
                "type": 'int or None',
                "description": 'Maximum number of peaks accessible in a cell.',
                "default": None
            },
            {
                "name": 'max_counts',
                "type": 'int or None',
                "description": 'Maximum total counts for a cell.',
                "default": None
            },
            {
                "name": 'inplace',
                "type": 'bool',
                "description": 'Modify in place.',
                "default": True
            },
        ],
    },
    # =============================================================================
    # ATAC TOOLS FUNCTIONS
    # =============================================================================
    {
        "name": 'scATAC_tl_lsi',
        "description": 'Latent Semantic Indexing (LSI) for ATAC data. LSI is the ATAC equivalent of PCA for RNA data. Should be run after TF-IDF normalization.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'n_comps',
                "type": 'int',
                "description": 'Number of LSI components to compute.',
                "default": 50
            },
            {
                "name": 'use_highly_variable',
                "type": 'bool or None',
                "description": 'Use highly variable peaks only.',
                "default": None
            },
            {
                "name": 'scale_embeddings',
                "type": 'bool',
                "description": 'Scale embeddings to unit variance.',
                "default": True
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    {
        "name": 'scATAC_tl_nucleosome_signal',
        "description": 'Calculate nucleosome signal from fragment sizes. The nucleosome signal is the ratio of mono-nucleosomal to nucleosome-free fragments, indicating chromatin quality.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'n',
                "type": 'float',
                "description": 'Number of fragments to sample.',
                "default": 1000000.0
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    {
        "name": 'scATAC_tl_tss_enrichment',
        "description": 'Calculate TSS (Transcription Start Site) enrichment score. TSS enrichment is a key quality metric for ATAC data, measuring chromatin accessibility around gene promoters.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'extend_upstream',
                "type": 'int',
                "description": 'Extend TSS region upstream.',
                "default": 1000
            },
            {
                "name": 'extend_downstream',
                "type": 'int',
                "description": 'Extend TSS region downstream.',
                "default": 1000
            },
            {
                "name": 'n_tss',
                "type": 'int',
                "description": 'Number of TSS to sample.',
                "default": 2000
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    # =============================================================================
    # ATAC PLOTTING FUNCTIONS
    # =============================================================================
    {
        "name": 'scATAC_pl_fragment_histogram',
        "description": 'Plot fragment size histogram. Shows the distribution of fragment sizes, which should show nucleosome banding patterns for good quality ATAC data.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'groupby',
                "type": 'str or None',
                "description": 'Column in obs to group by.',
                "default": None
            },
            {
                "name": 'log',
                "type": 'bool',
                "description": 'Log-scale y-axis.',
                "default": False
            },
            {
                "name": 'show',
                "type": 'bool',
                "description": 'Show plot.',
                "default": True
            },
            {
                "name": 'save',
                "type": 'str or None',
                "description": 'Path to save figure.',
                "default": None
            },
        ],
    },
    {
        "name": 'scATAC_pl_tss_enrichment',
        "description": 'Plot TSS enrichment profile.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'groupby',
                "type": 'str or None',
                "description": 'Column in obs to group by.',
                "default": None
            },
            {
                "name": 'show',
                "type": 'bool',
                "description": 'Show plot.',
                "default": True
            },
            {
                "name": 'save',
                "type": 'str or None',
                "description": 'Path to save figure.',
                "default": None
            },
        ],
    },
    # =============================================================================
    # MULTIMODAL PREPROCESSING FUNCTIONS
    # =============================================================================
    {
        "name": 'scMulti_pp_intersect_obs',
        "description": 'Intersect observations across modalities. Keeps only cells present in all modalities.',
        "required_parameters": [],
        "optional_parameters": [],
    },
    {
        "name": 'scMulti_pp_neighbors',
        "description": 'Compute neighbors graph for MuData.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'n_neighbors',
                "type": 'int',
                "description": 'Number of neighbors.',
                "default": 15
            },
            {
                "name": 'n_pcs',
                "type": 'int or None',
                "description": 'Number of PCs to use.',
                "default": None
            },
            {
                "name": 'use_rep',
                "type": 'str or None',
                "description": 'Representation to use.',
                "default": None
            },
            {
                "name": 'method',
                "type": 'str',
                "description": 'Method for computing connectivities.',
                "default": 'umap'
            },
            {
                "name": 'metric',
                "type": 'str',
                "description": 'Distance metric.',
                "default": 'euclidean'
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    # =============================================================================
    # MULTIMODAL TOOLS FUNCTIONS
    # =============================================================================
    {
        "name": 'scMulti_tl_umap',
        "description": 'UMAP embedding for MuData.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'min_dist',
                "type": 'float',
                "description": 'Minimum distance.',
                "default": 0.5
            },
            {
                "name": 'spread',
                "type": 'float',
                "description": 'Spread.',
                "default": 1.0
            },
            {
                "name": 'n_components',
                "type": 'int',
                "description": 'Number of components.',
                "default": 2
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    {
        "name": 'scMulti_tl_leiden',
        "description": 'Leiden clustering for MuData.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'resolution',
                "type": 'float',
                "description": 'Resolution parameter.',
                "default": 1.0
            },
            {
                "name": 'key_added',
                "type": 'str',
                "description": 'Key to add.',
                "default": 'leiden'
            },
            {
                "name": 'neighbors_key',
                "type": 'str or None',
                "description": 'Key for neighbors.',
                "default": None
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    {
        "name": 'scMulti_tl_mofa',
        "description": 'MOFA (Multi-Omics Factor Analysis) for multimodal integration. MOFA infers a set of latent factors that capture the major sources of variation across multiple modalities.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'n_factors',
                "type": 'int',
                "description": 'Number of factors to learn.',
                "default": 10
            },
            {
                "name": 'scale_views',
                "type": 'bool',
                "description": 'Scale views to unit variance.',
                "default": False
            },
            {
                "name": 'n_iterations',
                "type": 'int',
                "description": 'Number of iterations.',
                "default": 1000
            },
            {
                "name": 'convergence_mode',
                "type": 'str',
                "description": "Convergence mode ('fast', 'medium', 'slow').",
                "default": 'fast'
            },
            {
                "name": 'seed',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
            {
                "name": 'verbose',
                "type": 'bool',
                "description": 'Verbose output.',
                "default": False
            },
        ],
    },
    {
        "name": 'scMulti_tl_wnn',
        "description": 'Weighted Nearest Neighbors (WNN) integration. WNN learns cell-specific weights for each modality to compute a weighted combination of neighbors graphs.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'n_neighbors',
                "type": 'int',
                "description": 'Number of neighbors in final graph.',
                "default": 20
            },
            {
                "name": 'n_bandwidth_neighbors',
                "type": 'int',
                "description": 'Number of neighbors for bandwidth estimation.',
                "default": 20
            },
            {
                "name": 'n_multineighbors',
                "type": 'int',
                "description": 'Number of multi-neighbors.',
                "default": 200
            },
            {
                "name": 'key_added',
                "type": 'str',
                "description": 'Key to add results.',
                "default": 'wnn'
            },
            {
                "name": 'random_state',
                "type": 'int',
                "description": 'Random seed.',
                "default": 0
            },
        ],
    },
    # =============================================================================
    # MULTIMODAL PLOTTING FUNCTIONS
    # =============================================================================
    {
        "name": 'scMulti_pl_embedding',
        "description": 'Plot embedding for MuData.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'basis',
                "type": 'str',
                "description": 'Embedding basis.',
                "default": 'X_umap'
            },
            {
                "name": 'color',
                "type": 'str or list or None',
                "description": 'Variables to color by.',
                "default": None
            },
            {
                "name": 'show',
                "type": 'bool',
                "description": 'Show plot.',
                "default": True
            },
            {
                "name": 'save',
                "type": 'str or None',
                "description": 'Path to save figure.',
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_pl_umap',
        "description": 'Plot UMAP for MuData.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'color',
                "type": 'str or list or None',
                "description": 'Variables to color by.',
                "default": None
            },
            {
                "name": 'show',
                "type": 'bool',
                "description": 'Show plot.',
                "default": True
            },
            {
                "name": 'save',
                "type": 'str or None',
                "description": 'Path to save figure.',
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_pl_mofa',
        "description": 'Plot MOFA results: variance explained per factor and per modality.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'show',
                "type": 'bool',
                "description": 'Show plot.',
                "default": True
            },
            {
                "name": 'save',
                "type": 'str or None',
                "description": 'Path to save figure.',
                "default": None
            },
        ],
    },
    # =============================================================================
    # ADDITIONAL I/O AND UTILITY FUNCTIONS
    # =============================================================================
    {
        "name": 'scMulti_read_h5ad',
        "description": 'Read H5AD file as AnnData and optionally convert to MuData.',
        "required_parameters": [
            {
                "name": 'filename',
                "type": 'str',
                "description": 'Path to H5AD file.',
                "default": None
            },
        ],
        "optional_parameters": [
            {
                "name": 'mod',
                "type": 'str or None',
                "description": 'Modality name to assign when converting to MuData.',
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_pp_filter_obs',
        "description": 'Filter observations (cells) based on obs columns. Keeps cells that pass the filter.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'var',
                "type": 'str or None',
                "description": 'Column in obs to filter on.',
                "default": None
            },
            {
                "name": 'func',
                "type": 'callable or None',
                "description": 'Filter function.',
                "default": None
            },
        ],
    },
    {
        "name": 'scMulti_pp_filter_var',
        "description": 'Filter variables (features) based on var columns.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'var',
                "type": 'str or None',
                "description": 'Column in var to filter on.',
                "default": None
            },
            {
                "name": 'func',
                "type": 'callable or None',
                "description": 'Filter function.',
                "default": None
            },
        ],
    },
    {
        "name": 'scATAC_tl_get_gene_annotation_from_rna',
        "description": 'Get gene annotation from RNA modality for ATAC peak annotation.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'gene_name_key',
                "type": 'str',
                "description": 'Key in RNA .var for gene names.',
                "default": 'gene_ids'
            },
        ],
    },
    {
        "name": 'scATAC_tl_add_peak_annotation',
        "description": 'Add peak annotation (e.g., nearest gene, genomic region type) to ATAC data.',
        "required_parameters": [],
        "optional_parameters": [
            {
                "name": 'annotation',
                "type": 'DataFrame or None',
                "description": 'Annotation DataFrame with peak info.',
                "default": None
            },
        ],
    },
]

# Create a lookup dictionary for quick access
TOOL_LOOKUP = {tool["name"]: tool for tool in description}


def get_tool_names():
    """Return list of all tool names."""
    return [tool["name"] for tool in description]


def get_tool_by_name(name):
    """Get tool definition by name."""
    return TOOL_LOOKUP.get(name)
