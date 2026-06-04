"""
scRNA seq tools for atlas studies
"""

import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from typing import List

from src.tools_singlecell._type_coercion import (
    coerce_int, coerce_float, coerce_bool, coerce_str,
    coerce_str_list, coerce_int_list,
)

def _iter_batches(adata, batch_key: str):
    """
    Iterate over batches in an AnnData object.
    
    Yields
    ------
    batch_name : str
        Name of the current batch.
    adata_batch : AnnData
        Subset of adata for this batch (view, not copy).
    """
    for batch_name in adata.obs[batch_key].unique():
        mask = adata.obs[batch_key] == batch_name
        yield batch_name, adata[mask]

def scRNA_calculate_qc_metrics(
    adata,
    qc_vars=["mt", "ribo", "hb"],
    layer=None,
    use_raw=False,
    batch_key=None,
):
    """
    Perform quality control on the AnnData object.
    
    If batch_key is provided, QC metrics are computed per batch first, then on
    the full object. Generates separate violin and scatter plots per batch.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    qc_vars : Collection[str], optional (default: ["mt", "ribo", "hb"])
        Keys for boolean columns of .var which identify variables you could
        want to control for.
    layer : str or None, optional (default: None)
        If provided, use adata.layers[layer] for expression values.
    use_raw : bool, optional (default: False)
        If True, use adata.raw.X for expression values.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, computes QC
        per batch first, then on full object, with per-batch plots.

    Returns
    -------
    adata : AnnData
        AnnData with QC metrics in .obs and .var.
    """
    adata.obs_names_make_unique(join="-")
    qc_vars = coerce_str_list(qc_vars) or ["mt", "ribo", "hb"]
    layer = coerce_str(layer)
    use_raw = coerce_bool(use_raw, False)
    batch_key = coerce_str(batch_key)
    
    # === Compute QC gene annotations (on full object) ===
    if "mt" in qc_vars:
        mt_human = adata.var_names.str.startswith("MT-")
        mt_mouse = adata.var_names.str.startswith(("mt-", "Mt-"))
        adata.var["mt"] = mt_human | mt_mouse
        
        n_mt = adata.var["mt"].sum()
        if n_mt == 0:
            print(f"⚠️ WARNING: No mitochondrial genes found (checked MT-, mt-, Mt- prefixes).")
            print(f"   Sample gene names: {list(adata.var_names[:5])}")
        else:
            print(f"✓ Found {n_mt} mitochondrial genes")
            
    if "ribo" in qc_vars:
        adata.var["ribo"] = adata.var_names.str.startswith(("RPS", "RPL"))
        print(f"✓ Found {adata.var['ribo'].sum()} ribosomal genes")
        
    if "hb" in qc_vars:
        adata.var["hb"] = adata.var_names.str.contains("^HB[^(P)]")
        print(f"✓ Found {adata.var['hb'].sum()} hemoglobin genes")

    # === Compute QC metrics on full object (always needed) ===
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=qc_vars, layer=layer, 
        use_raw=use_raw, inplace=True)
    
    if batch_key:
        # === Generate per-batch plots ===
        batch_names = sorted(adata.obs[batch_key].unique().tolist())
        print(f"\n📊 Generating QC plots for {len(batch_names)} batches")
        for batch_name, batch_adata in _iter_batches(adata, batch_key):
            print(f"\n--- Batch: {batch_name} ({batch_adata.n_obs:,} cells) ---")
            
            # Per-batch plots with descriptive titles
            sc.pl.violin(
                batch_adata, 
                ["n_genes_by_counts", "total_counts", "pct_counts_mt"], 
                jitter=0.4, multi_panel=True,
                show=False
            )
            plt.suptitle(f"QC_Violin_{batch_name}", y=1.05)
            sc.pl.scatter(
                batch_adata, "total_counts", "n_genes_by_counts", 
                color="pct_counts_mt",
                title=f"QC_Scatter_{batch_name}",
                show=False
            )
    else:
        # Single batch or no batch key - just plot
        sc.pl.violin(
            adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt"], 
            jitter=0.4, multi_panel=True,
            show=False
        )
        plt.suptitle(f"QC_Violin", y=1.05)
        sc.pl.scatter(
            adata, "total_counts", "n_genes_by_counts", 
            color="pct_counts_mt",
            title=f"QC_Scatter",
            show=False
        )
    return adata

def scRNA_perform_qc_filtering(
    adata,
    min_genes=200,
    min_cells=3,
    batch_key=None,
):
    """
    Perform quality control filtering on the AnnData object.
    
    If batch_key is provided, reports filtering statistics per batch.
    Filtering is always performed on the combined object to maintain
    consistent gene sets across batches.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    min_genes : int, optional (default: 200)
        Minimum number of genes expressed required for a cell to pass filtering.
    min_cells : int, optional (default: 3)
        Minimum number of cells expressed required for a gene to pass filtering.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, reports
        per-batch filtering statistics.
        
    Returns
    -------
    adata : AnnData
        Filtered AnnData object.
    """
    min_genes = coerce_int(min_genes, 200)
    min_cells = coerce_int(min_cells, 3)
    batch_key = coerce_str(batch_key)
    
    n_cells_before = adata.n_obs
    n_genes_before = adata.n_vars
    batch_names = adata.obs[batch_key].unique().tolist() if batch_key else []
    
    if batch_key:
        per_batch_before = {b: (adata.obs[batch_key] == b).sum() for b in batch_names}
        print(f"\n📊 Pre-filtering cell counts per batch:")
        for b, n in per_batch_before.items():
            print(f"   {b}: {n:,} cells")
    
    # For genes: require expression in min_cells across ALL batches combined
    # Don't scale by n_batches - that's too aggressive
    print(f"\n🔍 Filtering: min_genes={min_genes}, min_cells={min_cells}")
    sc.pp.filter_cells(adata, min_genes=min_genes, inplace=True)
    sc.pp.filter_genes(adata, min_cells=min_cells, inplace=True)
    
    n_cells_after = adata.n_obs
    n_genes_after = adata.n_vars
    pct_cells = 100 * (n_cells_before - n_cells_after) / n_cells_before
    pct_genes = 100 * (n_genes_before - n_genes_after) / n_genes_before
    
    print(f"\n✓ Filtering complete:")
    print(f"   Cells: {n_cells_before:,} → {n_cells_after:,} ({pct_cells:.1f}% removed)")
    print(f"   Genes: {n_genes_before:,} → {n_genes_after:,} ({pct_genes:.1f}% removed)")
    
    if batch_key:
        print(f"\n📊 Post-filtering cell counts per batch:")
        for batch_name in batch_names:
            n_batch = (adata.obs[batch_key] == batch_name).sum()
            before = per_batch_before[batch_name]
            pct_removed = 100 * (before - n_batch) / before if before > 0 else 0
            print(f"   {batch_name}: {before:,} → {n_batch:,} ({pct_removed:.1f}% removed)")
    
    return adata

def scRNA_remove_high_mt_cells(
    adata,
    max_mt_pct=20,
):
    """
    Remove cells with a high percentage of mitochondrial reads. 
    Should be called per batch, with appropriate max_mt_pct for each batch.
    """
    max_mt_pct = coerce_float(max_mt_pct, 20.0)
    n_before = adata.n_obs
    adata = adata[adata.obs['pct_counts_mt'] < max_mt_pct].copy()
    print(f"✓ Removed {n_before - adata.n_obs:,} cells with MT% >= {max_mt_pct}")
    return adata

def scRNA_get_doublet_scores(
    adata,
    batch_key=None,
    threshold=0.3,
):
    """
    Compute doublet scores using Scrublet. Does NOT remove doublets.
    
    Calculates doublet scores for each cell and generates a score distribution plot.
    Use the plot to assess the threshold, then filter manually if needed:
        adata = adata[adata.obs['doublet_score'] < your_threshold]
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches for batch-aware doublet detection.
        If None, runs scrublet on entire dataset.
    threshold : float, optional (default: 0.3)
        Threshold for doublet score. Used only for reporting statistics.
        Does NOT filter cells - filter manually after inspecting the plot.
        
    Returns
    -------
    adata : AnnData
        AnnData with doublet scores in .obs['doublet_score'].
        Cells are NOT removed - use scores to filter manually.
    """
    batch_key = coerce_str(batch_key)
    n_before = adata.n_obs
    
    # Run scrublet (batch_key can be None for single-batch)
    sc.pp.scrublet(adata, batch_key=batch_key, threshold=threshold)
    
    if batch_key and batch_key in adata.obs.columns:
        batch_names = adata.obs[batch_key].unique().tolist()
        print(f"\n📊 Scrublet results per batch ({len(batch_names)} batches):")
        for batch_name in batch_names:
            batch_adata = adata[adata.obs[batch_key] == batch_name]
            n_doublets = batch_adata.obs['predicted_doublet'].sum()
            pct_doublets = 100 * n_doublets / len(batch_adata)
            print(f"   {batch_name}: {n_doublets:,} doublets ({pct_doublets:.1f}%)")
        
        # Plot score distribution - function auto-creates subplots per batch
        sc.pl.scrublet_score_distribution(adata, show=False)
        plt.suptitle("Scrublet_Batchwise", y=1.02)
    else:
        sc.pl.scrublet_score_distribution(adata, show=False)
        plt.suptitle("Scrublet", y=1.02)
    
    n_doublets_total = adata.obs['predicted_doublet'].sum()
    pct_doublets_total = 100 * n_doublets_total / n_before
    print(f"\n🔍 Detected doublets: {n_doublets_total:,} ({pct_doublets_total:.1f}%)")

    # remove labels predicting doublets
    adata.obs = adata.obs.drop(columns=['predicted_doublet'])
    
    return adata

def scRNA_normalize_data(
    adata,
    target_sum=1e4,
    default_layer="log1p_norm",
    batch_key=None,
):
    """
    Normalize the data using multiple methods and store in layers.
    
    If batch_key is provided, normalization is performed per batch (each batch 
    normalized to its own median). Otherwise performed on combined object.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with raw counts.
    target_sum : float or None, optional (default: None)
        Target sum for size factor normalization. If None, uses median count depth.
    default_layer : str, optional (default: "log1p_norm")
        Which normalization to use as adata.X for downstream analysis.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, normalizes
        each batch independently.
        
    Returns
    -------
    adata : AnnData
        Normalized AnnData with results stored in layers:
        - "counts": raw counts
        - "log1p_norm": shifted logarithm (good for dim reduction, DE)
    """
    target_sum = coerce_float(target_sum)
    default_layer = coerce_str(default_layer) or "log1p_norm"
    batch_key = coerce_str(batch_key)
    
    # Store raw counts
    if "counts" not in adata.layers:
        adata.layers["counts"] = adata.X.copy()
    
    if batch_key:
        # Per-batch normalization: normalize each batch to its own median
        # Pre-allocate output (same sparsity as input)
        if sparse.issparse(adata.X):
            normalized = sparse.lil_matrix(adata.X.shape, dtype=np.float32)
        else:
            normalized = np.zeros(adata.X.shape, dtype=np.float32)
        
        batch_names = adata.obs[batch_key].unique().tolist()
        for batch_name in batch_names:
            batch_mask = adata.obs[batch_key] == batch_name
            batch_idx = np.where(batch_mask)[0]
            batch_adata = adata[batch_mask]
            
            # Normalize and log1p for this batch
            result = sc.pp.normalize_total(batch_adata, target_sum=target_sum, inplace=False)
            batch_normalized = sc.pp.log1p(result["X"], copy=True)
            
            # Store back in correct positions
            normalized[batch_idx, :] = batch_normalized
            print(f"✓ Normalized batch: {batch_name} ({len(batch_idx):,} cells)")
        
        # Convert back to csr for efficient operations
        if sparse.issparse(adata.X):
            adata.layers["log1p_norm"] = normalized.tocsr()
        else:
            adata.layers["log1p_norm"] = normalized
    else:
        # Single normalization on entire dataset
        result = sc.pp.normalize_total(adata, target_sum=target_sum, inplace=False)
        adata.layers["log1p_norm"] = sc.pp.log1p(result["X"], copy=True)
        print(f"✓ Normalized dataset ({adata.n_obs:,} cells)")

    if default_layer in adata.layers:
        adata.X = adata.layers[default_layer].copy()
        print(f"→ adata.X set to '{default_layer}'")

    return adata
    

def scRNA_feature_selection(
    adata,
    n_top_genes=2000,
    batch_key=None,
):
    """
    Perform feature selection on the AnnData object.
    
    If batch_key is provided, HVGs are computed accounting for batch effects
    and per-batch HVG overlap statistics are reported.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    n_top_genes : int, optional (default: 2000)
        Number of highly variable genes to select.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, uses batch-aware
        HVG selection.
        
    Returns
    -------
    adata : AnnData
        AnnData with highly_variable genes marked in .var, subset to HVGs.
        Original data preserved in adata.raw.
    """
    n_top_genes = coerce_int(n_top_genes, 2000)
    batch_key = coerce_str(batch_key)
    
    if batch_key:
        print(f"\n🔬 Computing batch-aware HVGs ({batch_key})")

    sc.pp.highly_variable_genes(
        adata, 
        n_top_genes=n_top_genes, 
        batch_key=batch_key,
        inplace=True
    )
    sc.pl.highly_variable_genes(adata, show=False)

    # Save normalized data (all genes) as raw before subsetting
    adata.raw = adata.copy()
    
    # Subset to HVGs
    if batch_key and 'highly_variable_nbatches' in adata.var.columns:
        # Batch-aware: select genes HVG in > 1 batch
        var_select = adata.var.highly_variable_nbatches > 1
        var_genes = var_select.index[var_select]
        print(f"✓ Selected {len(var_genes)} HVGs (highly variable in > 1 batch)")
    else:
        # Single-batch: use highly_variable column
        var_genes = adata.var_names[adata.var.highly_variable]
        print(f"✓ Selected {len(var_genes)} HVGs")
    
    adata = adata[:, var_genes].copy()
    
    return adata

def scRNA_dimensionality_reduction(
    adata,
    n_components=100,
    batch_key=None,
    random_state=42,
):
    """
    Perform scaling, PCA, and optional batch correction (Harmony) on the AnnData object.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    n_components : int, optional (default: 100)
        Number of principal components to compute.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, runs Harmony integration.
    random_state : int, optional (default: 42)
        Random seed for reproducibility.
    """
    n_components = coerce_int(n_components, 100)
    batch_key = coerce_str(batch_key)
    random_state = coerce_int(random_state, 42)

    sc.pp.scale(adata, max_value=10)
    sc.pp.pca(adata, n_comps=n_components, random_state=random_state, svd_solver='arpack')
    sc.pl.pca_variance_ratio(adata, n_pcs=n_components, log=True, show=False)
    plt.title("PCA_Variance")
    
def scRNA_batch_correction(
    adata,
    method = "harmony", # harmony, scanorama
    batch_keys=List[str],
    random_state=42,
):
    """
    Perform batch correction on the AnnData object.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, runs batch correction.
    random_state : int, optional (default: 42)
        Random seed for reproducibility.
    """
    method = coerce_str(method) or "harmony"
    batch_keys = coerce_str_list(batch_keys)
    random_state = coerce_int(random_state, 42)
    
    if method == "harmony":
        if batch_keys:
            print(f"🔧 Running Harmony integration on {batch_keys}")
            import harmonypy
            harmony_out = harmonypy.run_harmony(
                adata.obsm['X_pca'], adata.obs, batch_keys, 
                random_state=random_state, max_iter_harmony=100
            )
            adata.obsm['X_pca_harmony'] = harmony_out.Z_corr
            adata.obsm['X_pca'] = adata.obsm['X_pca_harmony'].copy()
            print(adata.obsm['X_pca_harmony'].shape)
            print(adata.obsm['X_pca'].shape)
            print(f"✓ Harmony integration complete")
        else:
            print(f"⚠️ Batch key(s) are required for Harmony integration")
    elif method == "scanorama":
        # can pass only one batch key
        if batch_keys and len(batch_keys) == 1:
            batch_key = batch_keys[0]
            print(f"🔧 Running Scanorama integration on {batch_key}")
            
            # Scanorama requires contiguous batches - sort by batch key
            original_obs_names = adata.obs_names.tolist()
            sorted_idx = adata.obs[batch_key].sort_values().index
            adata = adata[sorted_idx].copy()
            print(f"   Sorted cells by {batch_key} for contiguous batches")
            
            sc.external.pp.scanorama_integrate(adata, key=batch_key)
            adata.obsm['X_pca'] = adata.obsm['X_scanorama']
            
            # Restore original order
            adata = adata[original_obs_names].copy()
            print(f"   Restored original cell order")
            print(f"✓ Scanorama integration complete")
        else:
            print(f"⚠️ Batch key(s) are required for Scanorama integration and only one batch key is supported")
    else:
        print(f"⚠️ Invalid method: {method}")
    
    return adata

def scRNA_clustering(
    adata,
    n_pcs=30,
    n_neighbors=15,
    resolution=0.5,
    batch_key=None,
    random_state=42,
):
    """
    Perform neighborhood graph construction, Leiden clustering, and UMAP on the AnnData object.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with PCA computed.
    n_pcs : int, optional (default: 30)
        Number of PCs to use for neighbor graph.
    n_neighbors : int, optional (default: 15)
        Number of neighbors for kNN graph.
    resolution : float, optional (default: 0.5)
        Resolution parameter for Leiden clustering.
    batch_key : str or None, optional (default: None)
        Column in adata.obs identifying batches. If provided, shows batch in UMAP.
    random_state : int, optional (default: 42)
        Random seed for reproducibility.
    """
    n_pcs = coerce_int(n_pcs, 30)
    n_neighbors = coerce_int(n_neighbors, 15)
    resolution = coerce_float(resolution, 0.5)
    batch_key = coerce_str(batch_key)
    random_state = coerce_int(random_state, 42)
    
    print(f"🔬 Running neighborhood graph construction with {n_neighbors} neighbors and {n_pcs} PCs")
    sc.pp.neighbors(adata, random_state=random_state, n_neighbors=n_neighbors, n_pcs=n_pcs)
    print(f"🔬 Running Leiden clustering with resolution {resolution}")
    sc.tl.leiden(adata, random_state=random_state, resolution=resolution)
    print(f"🔬 Running UMAP")
    sc.tl.umap(adata, random_state=random_state)
    
    n_clusters = adata.obs['leiden'].nunique()
    print(f"✓ Found {n_clusters} clusters (resolution={resolution})")
    
    if batch_key:
        sc.pl.umap(adata, color=['leiden', batch_key], legend_loc='on data', title=["UMAP_Clusters", f"UMAP_{batch_key}"], show=False)
    else:
        sc.pl.umap(adata, color=['leiden'], legend_loc='on data', title="UMAP_Clusters", show=False)

    return adata


def _run_cnmf_single(
    adata_subset,
    output_dir,
    components,
    n_iter,
    density_threshold,
    seed,
):
    """Run cNMF on a single subset. Returns (usage_df, spectra_tpm, top_genes, selected_k, stability)."""
    import os
    import pandas as pd
    from cnmf import cNMF
    
    os.makedirs(output_dir, exist_ok=True)
    run_name = "cNMF"  # Fixed name to avoid path issues
    
    # Subset to HVGs if not already done
    if 'highly_variable' in adata_subset.var.columns:
        hvg_mask = adata_subset.var['highly_variable']
        hvg_genes = adata_subset.var_names[hvg_mask].tolist()
        print(f"   Using {len(hvg_genes)} HVGs from highly_variable column")
    else:
        hvg_genes = adata_subset.var_names.tolist()
        print(f"   Using all {len(hvg_genes)} genes (no highly_variable column)")
    
    # Write counts file
    counts_file = os.path.join(output_dir, "counts.h5ad")
    tmp_adata = adata_subset.copy()
    if "counts" in adata_subset.layers:
        tmp_adata.X = adata_subset.layers["counts"]
    tmp_adata.write_h5ad(counts_file)
    del tmp_adata
    print(f"   Wrote counts to {counts_file}")
    
    # Write genes file (HVGs only)
    genes_file = os.path.join(output_dir, "hvgs.txt")
    with open(genes_file, 'w') as f:
        f.write('\n'.join(hvg_genes))
    
    # Run cNMF
    print(f"   Initializing cNMF (K={components})...")
    cnmf_obj = cNMF(output_dir=output_dir, name=run_name)
    cnmf_obj.prepare(
        counts_fn=counts_file,
        components=components,
        n_iter=n_iter,
        seed=seed,
        genes_file=genes_file,
    )
    
    # Factorize (single worker to avoid numpy/pyarrow multiprocessing issues)
    print(f"   Factorizing ({n_iter} iterations)...")
    cnmf_obj.factorize(worker_i=0, total_workers=1)
    
    print(f"   Combining results...")
    cnmf_obj.combine()
    
    # K selection plot
    cnmf_obj.k_selection_plot()
    
    # Auto-select K based on highest stability
    stats_file = os.path.join(output_dir, run_name, f"{run_name}.k_selection_stats.txt")
    if not os.path.exists(stats_file):
        raise FileNotFoundError(f"cNMF stats file not found: {stats_file}. Check cNMF output in {output_dir}/{run_name}/")
    
    stats = pd.read_csv(stats_file, sep='\t', index_col=0)
    selected_k = int(stats['stability'].idxmax())
    stability = stats.loc[selected_k, 'stability']
    print(f"   Auto-selected K={selected_k} (stability={stability:.3f})")
    
    # Consensus
    cnmf_obj.consensus(k=selected_k, density_threshold=density_threshold)
    
    # Load results
    usage, spectra_scores, spectra_tpm, top_genes = cnmf_obj.load_results(
        K=selected_k, density_threshold=density_threshold
    )
    
    return usage, spectra_tpm, top_genes, selected_k, stability


def scRNA_cnmf_factorization(
    adata,
    cell_type_key='leiden',
    output_dir="./cnmf_results",
    components=[5, 10, 15, 20],
    n_iter=100,
    density_threshold=0.1,
    seed=42,
):
    """
    Run consensus NMF (cNMF) per cell type to identify gene expression programs.
    
    Assumes adata is already subset to HVGs from scRNA_feature_selection.
    Uses raw counts from adata.layers['counts'].
    Auto-selects K per cell type based on highest stability.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with counts in .layers['counts'] and subset to HVGs.
    cell_type_key : str
        Column in adata.obs containing cell type annotations.
    output_dir : str
        Directory to write cNMF output files.
    components : list of int, optional (default: [5, 10, 15, 20])
        K values (number of programs) to test.
    n_iter : int, optional (default: 100)
        Number of NMF iterations per K.
    density_threshold : float, optional (default: 0.1)
        Local density threshold for consensus clustering.
    seed : int, optional (default: 42)
        Random seed for reproducibility.
        
    Returns
    -------
    adata : AnnData
        AnnData with cNMF results stored in:
        - .uns['cnmf'][cell_type]: dict with spectra, top_genes, k, stability
        - .obs['{cell_type}_GEP{i}']: usage per program per cell type
    """
    import os
    
    cell_type_key = coerce_str(cell_type_key)
    output_dir = coerce_str(output_dir)
    components = coerce_int_list(components) or [5, 10, 15, 20]
    n_iter = coerce_int(n_iter, 100)
    density_threshold = coerce_float(density_threshold, 0.1)
    seed = coerce_int(seed, 42)
    
    os.makedirs(output_dir, exist_ok=True)
    
    cell_types = adata.obs[cell_type_key].unique().tolist()
    n_hvgs = adata.n_vars
    print(f"🔬 Running cNMF per cell type ({len(cell_types)} types, {n_hvgs:,} HVGs)")
    print(f"   Output directory: {output_dir}")
    
    # Initialize storage
    adata.uns['cnmf'] = {}
    
    for ct in cell_types:
        ct_mask = adata.obs[cell_type_key] == ct
        ct_adata = adata[ct_mask]
        n_cells = ct_adata.n_obs
        
        print(f"\n{'='*50}")
        print(f"📊 {ct} ({n_cells:,} cells)")
        print(f"{'='*50}")
        
        if n_cells < 50:
            print(f"⚠️ Skipping {ct}: too few cells (<50)")
            continue
        
        # Create subdirectory for this cell type
        ct_safe = ct.replace(' ', '_').replace('/', '_')
        ct_output_dir = os.path.join(output_dir, ct_safe)
        
        # Run cNMF
        usage, spectra_tpm, top_genes, selected_k, stability = _run_cnmf_single(
            ct_adata, ct_output_dir, components, n_iter, density_threshold, seed
        )
        
        print(f"✓ {ct}: K={selected_k} (stability={stability:.3f})")
        
        # Store results in uns
        adata.uns['cnmf'][ct] = {
            'spectra': spectra_tpm.values,
            'spectra_genes': spectra_tpm.columns.tolist(),
            'top_genes': {f"GEP{i}": top_genes.iloc[:, i].tolist() for i in range(top_genes.shape[1])},
            'k': selected_k,
            'stability': stability,
        }
        
        # Store usage in obs (only for cells of this type)
        usage_aligned = usage.loc[ct_adata.obs_names].values
        for i in range(selected_k):
            col_name = f"{ct_safe}_GEP{i}"
            adata.obs[col_name] = np.nan
            adata.obs.loc[ct_mask, col_name] = usage_aligned[:, i]
    
    # Summary
    print(f"\n{'='*50}")
    print(f"✓ cNMF complete for {len(adata.uns['cnmf'])} cell types")
    for ct, res in adata.uns['cnmf'].items():
        print(f"   {ct}: K={res['k']} (stability={res['stability']:.3f})")
    
    return adata

def scRNA_infercnv(
    adata,
    cell_type_key,
    reference_cat,
    tumor_cell_types,
    batch_key=None,
    window_size=250,
):
    """
    Run inferCNV to identify tumor vs normal cells based on CNV profiles.
    
    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with cell type annotations.
    cell_type_key : str
        Column in adata.obs containing cell type annotations.
    reference_cat : list of str
        Cell types to use as reference "normal" cells (e.g., immune cells).
    tumor_cell_types : list of str
        Cell types to classify as tumor (e.g., ["Epithelial cell"]).
    batch_key : str or None, optional
        Column in adata.obs for batch. If provided, generates per-batch plots.
    window_size : int, optional (default: 250)
        Window size for smoothing.
        
    Returns
    -------
    adata : AnnData
        AnnData with .obs['cnv_score'] and .obs['cnv_status'].
    """
    import infercnvpy as cnv
    
    cell_type_key = coerce_str(cell_type_key)
    reference_cat = coerce_str_list(reference_cat)
    tumor_cell_types = coerce_str_list(tumor_cell_types)
    batch_key = coerce_str(batch_key)
    window_size = coerce_int(window_size, 250)
    
    # Add genomic positions if missing
    if not all(col in adata.var.columns for col in ['chromosome', 'start', 'end']):
        cnv.io.genomic_position_from_biomart(adata)
    
    # Run inferCNV and compute score
    cnv.tl.infercnv(adata, reference_key=cell_type_key, reference_cat=reference_cat, window_size=window_size)
    cnv.tl.cnv_score(adata)
    
    # Classify tumor vs normal
    adata.obs["cnv_status"] = "normal"
    adata.obs.loc[adata.obs[cell_type_key].isin(tumor_cell_types), "cnv_status"] = "tumor"
    
    # Plot per batch or full dataset
    if batch_key:
        for batch_name in adata.obs[batch_key].unique():
            batch_adata = adata[adata.obs[batch_key] == batch_name]
            
            cnv.pl.chromosome_heatmap(batch_adata, groupby=cell_type_key, show=False)
            plt.suptitle(f"CNV_Heatmap_{batch_name}", y=1.02)
            
            if 'X_umap' in adata.obsm:
                fig, axes = plt.subplots(1, 2, figsize=(12, 5))
                sc.pl.umap(batch_adata, color="cnv_score", ax=axes[0], show=False)
                sc.pl.umap(batch_adata, color="cnv_status", ax=axes[1], show=False)
                fig.suptitle(f"CNV_UMAP_{batch_name}")
                plt.tight_layout()
    else:
        cnv.pl.chromosome_heatmap(adata, groupby=cell_type_key, show=False)
        if 'X_umap' in adata.obsm:
            sc.pl.umap(adata, color=["cnv_score", "cnv_status"], show=False)
    
    return adata
