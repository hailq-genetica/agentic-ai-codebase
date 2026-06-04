import snapatac2 as snap
import numpy as np
import matplotlib.pyplot as plt
import os

from src.tools_singlecell._type_coercion import (
    coerce_int, coerce_float, coerce_bool, coerce_str,
    coerce_str_list, coerce_int_list,
)

def scATAC_calculate_qc_metrics(adata_atac):
    """
    Calculate QC metrics for a scATAC-seq dataset.
    """

    snap.metrics.summary_by_chrom(adata_atac)

    # fragment size distribution
    print("Calculating fragment size distribution...")
    snap.metrics.frag_size_distr(adata_atac)
    fig1 = snap.pl.frag_size_distr(adata_atac, show=False, interactive=False)
    fig1.update_layout(
                title={
                'text' : "scATAC_fragment_size_dist",
                'x': 0.5,
                'xanchor': 'center'
            })

    # nucleosome signal
    print("Calculating nucleosome signal...")
    fragments = adata_atac.obsm['fragment_paired']

    # If the values are fragment sizes, we can compute directly:
    nucleosome_signal = []
    for i in range(fragments.shape[0]):
        row = fragments[i]
        sizes = row.data  # the non-zero values
        
        if len(sizes) == 0:
            nucleosome_signal.append(np.nan)
            continue
        
        nfr = np.sum(sizes < 147)
        mono = np.sum((sizes >= 147) & (sizes <= 294))
        ratio = mono / nfr if nfr > 0 else np.nan
        nucleosome_signal.append(ratio)

    adata_atac.obs['nucleosome_signal'] = nucleosome_signal

    # tss enrichment
    print("Calculating TSS enrichment...")
    snap.metrics.tsse(adata_atac, snap.genome.hg38)
    fig2 = snap.pl.tsse(adata_atac, interactive=False, show=False)
    fig2.update_layout(
                title={
                'text' : "scATAC_tss_enrichment",
                'x': 0.5,
                'xanchor': 'center'
            })

    # violin plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    possible = [
            ('n_fragment', 'n_fragments'),
            ('tsse', 'TSS_enrichment'),
            ('nucleosome_signal', 'nucleosome_signal'),
        ]
    metrics = [(col, title) for col, title in possible if col in adata_atac.obs.columns]
        
    for ax, (col, title) in zip(axes, metrics):
        data = adata_atac.obs[col].dropna().values.astype(float)
        
        # Violin
        parts = ax.violinplot(data, positions=[1], showmedians=False,
                                showextrema=False, widths=0.8)
        for pc in parts['bodies']:
            pc.set_facecolor('#D43F3A')
            pc.set_edgecolor('black')
            pc.set_linewidth(0.5)
            pc.set_alpha(0.6)
        
        # Jitter points
        jitter = np.random.normal(0, 0.12, size=len(data))
        ax.scatter(1 + jitter, data, c='black', s=0.5, 
                    alpha=0.2, rasterized=True, linewidths=0)
        
        # Styling
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0.2, 1.8)
        ax.set_xticks([])
        ax.tick_params(axis='y', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.tight_layout()

    # # frip
    # print("Calculating FRiP...")
    # snap.metrics.frip(adata_atac)
    # fig3 = snap.pl.frip(adata_atac, show=False)
    # fig3.set_title("scATAC_frip")

    print(adata_atac)
    return adata_atac

def scATAC_qc_filter_cells(adata_atac, min_counts=None, min_tsse=None, max_counts=None, max_nucleosome_signal=None):
    min_counts = coerce_int(min_counts)
    min_tsse = coerce_float(min_tsse)
    max_counts = coerce_int(max_counts)
    max_nucleosome_signal = coerce_float(max_nucleosome_signal)
    
    print("Filtering cells...")
    # min_counts, max_counts, min_tsse decided based on density plot.
    # can also be decided based on violin plot.
    snap.pp.filter_cells(adata_atac, min_counts=min_counts, min_tsse=min_tsse, max_counts=max_counts)

    # max_nucleosome_signal decided based on violin plot.
    if max_nucleosome_signal is not None:
        adata_atac = adata_atac[adata_atac.obs['nucleosome_signal'] < max_nucleosome_signal]

    print(adata_atac)
    return adata_atac

def scATAC_calculate_tiles(adata_atac):
    print("Calculating tiles...")
    # this step adds n_vars
    snap.pp.add_tile_matrix(adata_atac)
    print(adata_atac)
    return adata_atac

def scATAC_feature_selection(adata_atac, n_features=250000):
    n_features = coerce_int(n_features, 250000)
    print("Selecting features...")
    snap.pp.select_features(adata_atac, n_features=n_features, inplace=True)
    print(adata_atac)
    return adata_atac

def scATAC_doublet_detection(adata_atac):
    print("Detecting doublets...")
    snap.pp.scrublet(adata_atac, inplace=True)
    fig, ax = plt.subplots()
    ax.hist(adata_atac.obs['doublet_probability'], bins=100)
    ax.set_xlabel('Doublet Probability')
    ax.set_ylabel('Number of Cells')
    ax.set_title('scATAC_doublet_detection')
    print(adata_atac)
    return adata_atac

def scATAC_filter_doublets(adata_atac, threshold=0.5):
    threshold = coerce_float(threshold, 0.5)
    print("Filtering doublets...")
    snap.pp.filter_doublets(adata_atac, probability_threshold=threshold, inplace=True)
    print(adata_atac)
    return adata_atac

def scATAC_dimensionality_reduction(adata_atac, n_comps=100):
    n_comps = coerce_int(n_comps, 100)
    print("Performing dimensionality reduction using spectral embedding...")
    snap.tl.spectral(adata_atac, n_comps=n_comps)

    # --- Eigenvalue elbow plot (analogous to PCA variance plot) ---
    eigenvalues = adata_atac.uns.get("spectral_eigenvalue", None)
    if eigenvalues is not None:
        eigenvalues = np.asarray(eigenvalues)
        n_display = min(len(eigenvalues), n_comps)
        components = np.arange(1, n_display + 1)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Left: raw eigenvalues
        axes[0].plot(components, eigenvalues[:n_display], "o-", markersize=3, linewidth=1)
        axes[0].set_xlabel("Component")
        axes[0].set_ylabel("Eigenvalue")
        axes[0].set_title("Spectral Eigenvalues (Elbow Plot)")
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)

        # Right: cumulative proportion of total eigenvalue sum
        total = eigenvalues[:n_display].sum()
        if total > 0:
            cum_prop = np.cumsum(eigenvalues[:n_display]) / total
            axes[1].plot(components, cum_prop, "o-", markersize=3, linewidth=1, color="tab:orange")
            axes[1].set_xlabel("Component")
            axes[1].set_ylabel("Cumulative Proportion")
            axes[1].set_title("Cumulative Eigenvalue Proportion")
            axes[1].axhline(0.9, ls="--", color="grey", lw=0.8, label="90%")
            axes[1].legend(fontsize=9)
            axes[1].spines["top"].set_visible(False)
            axes[1].spines["right"].set_visible(False)

        fig.tight_layout()
    else:
        print("Warning: spectral_eigenvalue not found in adata_atac.uns – skipping elbow plot.")

    print(adata_atac)
    return adata_atac

def scATAC_batch_correction(adata_atac, batch_key, method="harmony"):
    batch_key = coerce_str(batch_key)
    method = coerce_str(method) or "harmony"
    print("Performing batch correction...")
    if method == "harmony":
        snap.pp.harmony(adata_atac, batch_key=batch_key)
    elif method == "scanorama":
        snap.pp.scanorama(adata_atac, batch_key=batch_key)
    else:
        print("Invalid method. Please choose either 'harmony' or 'scanorama'.")
    print(adata_atac)
    return adata_atac

def scATAC_clustering(adata_atac, n_comps=2, n_neighbors=50, resolution=0.5):
    n_comps = coerce_int(n_comps, 2)
    n_neighbors = coerce_int(n_neighbors, 50)
    resolution = coerce_float(resolution, 0.5)
    print("Performing KNN+Leiden clustering...")
    snap.pp.knn(adata_atac, n_neighbors=n_neighbors)
    snap.tl.leiden(adata_atac, resolution=resolution)

    print("Performing UMAP...")
    snap.tl.umap(adata_atac, n_comps=n_comps, random_state=42)
    snap.pl.umap(adata_atac, color=["leiden"], interactive=False)
    print(adata_atac)
    return adata_atac

# annotate cell types

def scATAC_identify_marker_peaks(adata_atac, cell_type_key, output_dir):
    cell_type_key = coerce_str(cell_type_key) or "leiden"
    output_dir = coerce_str(output_dir) or "."
    snap.tl.macs3(adata_atac, groupby=cell_type_key)
    peaks = snap.tl.merge_peaks(adata_atac.uns['macs3'], snap.genome.hg38)
    peaks.to_csv(os.path.join(output_dir, "marker_peaks.csv"))

    peak_mat = snap.pp.make_peak_matrix(adata_atac, use_rep=peaks['Peaks'])
    peak_mat.to_csv(os.path.join(output_dir, "peak_mat.csv"))

    marker_peaks = snap.tl.marker_regions(peak_mat, groupby=cell_type_key, pvalue=0.01)
    marker_peaks.to_csv(os.path.join(output_dir, "marker_peaks.csv"))

    fig1 = snap.pl.regions(peak_mat, groupby=cell_type_key, peaks=marker_peaks, interactive=False, show=False)
    fig1.update_layout(
                title={
                'text' : "scATAC_marker_peaks",
                'x': 0.5,
                'xanchor': 'center'
            })

    motifs = snap.tl.motif_enrichment(motifs=snap.datasets.cis_bp(unique=True), regions=marker_peaks, genome_fasta=snap.genome.hg38)
    motifs.to_csv(os.path.join(output_dir, "motifs.csv"))

    fig2 =snap.pl.motif_enrichment(motifs, max_fdr=0.0001, height=2000, interactive=False, show=False)
    fig2.update_layout(
                title={
                'text' : "scATAC_motif_enrichment",
                'x': 0.5,
                'xanchor': 'center'
            })
    print(adata_atac)
    return adata_atac


def scATAC_analyze_subset():
    # TODO: needs completion.
    pass

