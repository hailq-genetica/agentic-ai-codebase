# data/

Input datasets for the agent. Place data files here according to the paths set in each config YAML.

## HAI experiments

Each dataset lives in its own subdirectory. Expected structure (mirroring `config/hai/*.yaml`):

```
data/
  <dataset>/
    final_objects/
      <dataset>_scrna.h5ad        # scRNA-seq AnnData object
      <dataset>_scatac.h5ad       # scATAC-seq AnnData object
    <dataset>_scatac_with_fragments.h5ad  # scATAC backed with fragment file (scatac_snap_path)
    DATASET.md                    # dataset description (dataset_path)
```

Datasets: `jyates_eac`, `jfu_brca`, `epimenta_liposarcoma`

## HTAN experiments

All HTAN data lives under a shared root. Expected structure (mirroring `config/htan/opus-4-6/*/`):

```
data/datasets-mt/htan_datasets/results/
  scrna/
    <CANCER_TYPE>/
      final_combined_adata_<CANCER_TYPE>_anonymised.h5ad               # input for cancersite/cancertype annotation
      final_combined_adata_<CANCER_TYPE>_with_cancertype_sitetype.h5ad # input for celltype annotation
      final_combined_adata_<CANCER_TYPE>_with_cancertype_sitetype_celltype.h5ad  # input for molecular/pathology tasks
  scatac/
    <CANCER_TYPE>/
      final_combined_adata_<CANCER_TYPE>_anonymised.h5ad
      final_combined_adata_<CANCER_TYPE>_with_cancertype_sitetype.h5ad
      final_combined_adata_<CANCER_TYPE>_with_cancertype_sitetype_celltype.h5ad
      final_combined_adata_<CANCER_TYPE>_backed.h5ad                   # backed AnnData with fragment file (scatac_snap_path)
  cnmf/
    <CANCER_TYPE>/
      Tumor/
        usage.csv                 # cNMF usage matrix (cells × programs)
        spectra_scores.csv        # cNMF spectra scores (genes × programs)
        top_genes.csv             # top genes per program
```

Cancer types: `BRCA`, `CESC`, `COADREAD`, `GBM`, `HGSOC`, `HNSC`, `PAAD`, `SKCM`, `UCEC`

> cNMF files are only required for molecular/pathology tasks (those configs include `cnmf_*_path` fields).
