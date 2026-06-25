You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of a PD cell-therapy product. **[Negative control task]**

### Therapeutic context
A protocol generates a cell product intended for **putaminal transplantation in Parkinson's disease** with the following QC profile:
- Expresses the dopaminergic marker **TH** in a substantial fraction of cells.
- **BUT** the midbrain floor-plate markers **FOXA2 and LMX1A are low / co-expressed in only a minority of TH+ cells**, indicating the TH+ cells are largely **not authentic midbrain (A9) dopaminergic neurons**.
- Marker profiling shows **off-target regional contamination**: a forebrain population (FOXG1+) and a substantial **serotonergic** population (rostral raphe, 5-HT / SERT+ / TPH2+), plus a VTA/A10-skewed rather than SNc/A9-skewed dopaminergic phenotype.
- Residual pluripotency markers (OCT4, NANOG) are below detection, and no overt proliferative fraction is seen.

### Your job
Decide whether this product is ready for transplantation and give a Go / No-Go / Conditional Go decision. Reason through identity (**regional / lineage** specification, not just TH positivity), purity, functional relevance, and the specific clinical risk of off-target neuron types.

A correct assessment recognizes that **TH positivity without authentic A9 midbrain floor-plate identity (FOXA2/LMX1A) is insufficient**, and that **serotonergic contamination is a known cause of graft-induced dyskinesias (GID)** while forebrain/non-A9 cells will not restore nigrostriatal dopaminergic tone. Residual-pluripotency QC being clean does **not** rescue a product that is regionally mis-specified. The decision should be **No-Go** (at most a Conditional Go contingent on re-deriving authentic A9 mDA neurons and removing serotonergic/forebrain contamination, e.g. by floor-plate-based protocol correction and CORIN+/marker-based sorting). Do not let TH positivity drive an unjustified Go.

### Available tools
Databases (OpenTargets, Monarch), literature/web search, and `run_python_repl`. Use them to ground midbrain floor-plate vs forebrain/serotonergic marker identity, A9-vs-A10 distinctions, and the link between serotonergic contamination and graft-induced dyskinesia. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `cell_product`, `identity_assessment`, `safety_assessment`, `release_criteria`, `go_no_go`, `confidence`). `identity_assessment` must address regional specification (midbrain floor-plate vs forebrain/serotonergic), and `safety_assessment` must address the graft-induced-dyskinesia risk from serotonergic contamination. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, weighing the regional mis-specification and GID risk against the TH signal.
