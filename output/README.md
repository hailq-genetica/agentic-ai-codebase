# output/

Agent run results. Each run creates a timestamped subdirectory under the `output_base_dir` set in the config.

## Directory structure

**HAI experiments** (`output_base_dir: output/`):
```
output/
  <name>/                        # --name argument passed to run_agent.py (if provided)
    agent_<YYYYMMDD_HHMMSS>/     # one directory per run
      agent.log
      plot_*.png
      verification_notebook.ipynb
      result_rna.h5ad            # saved scRNA-seq AnnData (if modified)
      result_atac.h5ad           # saved scATAC-seq AnnData (if modified)
      result_combined.h5ad       # saved multiome AnnData (if modified)
```

**HTAN experiments** (`output_base_dir: output/<cancer_type>/<analysis_type>/`):
```
output/
  <cancer_type>/                 # e.g. brca, ccrcc, mm
    <analysis_type>/             # e.g. cancersite_annotation, celltype_annotation, molecular_er_luminal
      agent_<YYYYMMDD_HHMMSS>/
        agent.log
        plot_*.png
        verification_notebook.ipynb
        result_rna.h5ad
        result_atac.h5ad
```

## Run directory contents

| File | Description |
|------|-------------|
| `agent.log` | Full agent execution log including tool calls and model responses |
| `plot_*.png` | Figures generated during the run |
| `verification_notebook.ipynb` | Jupyter notebook audit trail of the complete execution |
| `result_rna.h5ad` | Final scRNA-seq AnnData object with agent-added annotations |
| `result_atac.h5ad` | Final scATAC-seq AnnData object with agent-added annotations |
| `result_combined.h5ad` | Final multiome AnnData object (when `scatac_snap_path` is set) |
