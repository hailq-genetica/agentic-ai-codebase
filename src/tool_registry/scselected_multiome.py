"""
Tool registry for scselected multiome (scRNA + scATAC) tools.

Tools for joint analysis of paired RNA and ATAC data.
Category: scselected_multiome
Implementation: src.tool_scselected.multiome
"""

description = [
    {
        "name": "scRNA_scATAC_perform_joint_embedding",
        "description": "Perform joint embedding of paired scRNA-seq and scATAC-seq data using SnapATAC2 multi_spectral. Computes a shared latent space and generates a UMAP colored by cell type. Requires both adata_rna and adata_atac to be loaded.",
        "required_parameters": [],
        "optional_parameters": [],
        "is_plotting": True,
    },
]
