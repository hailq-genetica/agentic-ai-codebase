"""
tool_singlecellselected - Curated subset of single-cell analysis tools.

This package provides a limited, curated set of single-cell tools for common
workflows. For the full set of scanpy tools, use src.tools_singlecell instead.

scRNA Tools:
- scRNA_calculate_qc_metrics: Calculate QC metrics (mt%, ribo%, etc.)
- scRNA_perform_qc_filtering: Filter cells/genes based on QC
- scRNA_remove_high_mt_cells: Remove cells with high mitochondrial reads
- scRNA_get_doublet_scores: Compute doublet scores (no removal)
- scRNA_normalize_data: Normalize with multiple methods
- scRNA_feature_selection: Select highly variable genes
- scRNA_dimensionality_reduction: PCA
- scRNA_batch_correction: Harmony/Scanorama batch correction
- scRNA_clustering: Leiden clustering + UMAP
- scRNA_cnmf_factorization: cNMF gene expression programs
- scRNA_infercnv: Copy number variation analysis

scATAC Tools (using SnapATAC2):
- scATAC_calculate_qc_metrics: Calculate QC metrics (fragment size, nucleosome signal, TSS enrichment)
- scATAC_qc_filter_cells: Filter cells based on QC metrics
- scATAC_calculate_tiles: Add tile matrix (genomic bins)
- scATAC_feature_selection: Select top features by variability
- scATAC_doublet_detection: Detect doublets using Scrublet
- scATAC_filter_doublets: Remove detected doublets
- scATAC_dimensionality_reduction: Spectral embedding
- scATAC_batch_correction: Harmony/Scanorama batch correction
- scATAC_clustering: KNN + Leiden clustering + UMAP
- scATAC_identify_marker_peaks: Peak calling + marker regions + motif enrichment
"""

from .scrna import (
    scRNA_calculate_qc_metrics,
    scRNA_perform_qc_filtering,
    scRNA_remove_high_mt_cells,
    scRNA_get_doublet_scores,
    scRNA_normalize_data,
    scRNA_feature_selection,
    scRNA_dimensionality_reduction,
    scRNA_batch_correction,
    scRNA_clustering,
    scRNA_cnmf_factorization,
    scRNA_infercnv,
)

from .scatac import (
    scATAC_calculate_qc_metrics,
    scATAC_qc_filter_cells,
    scATAC_calculate_tiles,
    scATAC_feature_selection,
    scATAC_doublet_detection,
    scATAC_filter_doublets,
    scATAC_dimensionality_reduction,
    scATAC_batch_correction,
    scATAC_clustering,
    scATAC_identify_marker_peaks,
)

__all__ = [
    # scRNA tools
    "scRNA_calculate_qc_metrics",
    "scRNA_perform_qc_filtering",
    "scRNA_remove_high_mt_cells",
    "scRNA_get_doublet_scores",
    "scRNA_normalize_data",
    "scRNA_feature_selection",
    "scRNA_dimensionality_reduction",
    "scRNA_batch_correction",
    "scRNA_clustering",
    "scRNA_cnmf_factorization",
    "scRNA_infercnv",
    # scATAC tools
    "scATAC_calculate_qc_metrics",
    "scATAC_qc_filter_cells",
    "scATAC_calculate_tiles",
    "scATAC_feature_selection",
    "scATAC_doublet_detection",
    "scATAC_filter_doublets",
    "scATAC_dimensionality_reduction",
    "scATAC_batch_correction",
    "scATAC_clustering",
    "scATAC_identify_marker_peaks",
]
