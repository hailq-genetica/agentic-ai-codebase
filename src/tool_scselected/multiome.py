import snapatac2 as snap
import anndata as ad
import scanpy as sc
import pandas as pd
import scvi

def scRNA_scATAC_perform_joint_embedding(adata_rna, adata_atac):
    embedding = snap.tl.multi_spectral([adata_rna, adata_atac], features=None)[1]
    adata_atac.obsm['X_joint'] = embedding
    snap.tl.umap(adata_atac, use_rep='X_joint')
    fig = snap.pl.umap(adata_atac, color="cell_type", interactive=False, show=False)
    fig.update_layout(
                title={
                'text' : "scRNA_scATAC_joint_embedding",
                'x': 0.5,
                'xanchor': 'center'
            })
    print(adata_atac)
    print(adata_rna)
    return adata_atac

def scRNA_to_annotate_scATAC_clusters_using_scVI(adata_rna, adata_atac):
    """
    scRNA is annotated with cell types, scATAC is in the cell-by-bin matrix form.
    This is needed when scRNA and scATAC are not paired. Not needed for multiome data.
    """
    query = snap.pp.make_gene_matrix(adata_atac, gene_anno=snap.genome.hg38)
    query.obs['cell_type'] = pd.NA
    data = ad.concat([adata_rna, query],
        join='inner',
        label='batch',
        keys=["reference", "query"],
        index_unique='_',
    )
    sc.pp.filter_genes(data, min_cells=5)
    sc.pp.highly_variable_genes(
        data,
        n_top_genes = 5000,
        flavor="seurat_v3",
        batch_key="batch",
        subset=True
    )

    scvi.model.SCVI.setup_anndata(data, batch_key="batch")
    vae = scvi.model.SCVI(
        data,
        n_layers=2,
        n_latent=30,
        gene_likelihood="nb",
        dispersion="gene-batch",
    )

    vae.train(max_epochs=1000, early_stopping=True)
    ax = vae.history['elbo_train'][1:].plot()
    vae.history['elbo_validation'].plot(ax=ax)

    data.obs["celltype_scanvi"] = 'Unknown'
    ref_idx = data.obs['batch'] == "reference"
    data.obs["celltype_scanvi"][ref_idx] = data.obs['cell_type'][ref_idx]

    lvae = scvi.model.SCANVI.from_scvi_model(
        vae,
        adata=data,
        labels_key="celltype_scanvi",
        unlabeled_category="Unknown",
    )

    lvae.train(max_epochs=1000, n_samples_per_label=100)
    lvae.history['elbo_train'][1:].plot()

    # TODO: needs completion.











