You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of a PD cell-therapy product. **[Negative control task]**

### Therapeutic context
A protocol generates a cell product intended for **transplantation in Parkinson's disease** with the following QC profile:
- Expresses the dopaminergic marker **TH** in a substantial fraction of cells.
- **BUT** shows **high residual OCT4 and NANOG expression** (pluripotency markers well above detection thresholds), and an unresolved fraction of proliferative cells (Ki-67 positive).
- Midbrain floor-plate markers (FOXA2, LMX1A) only partially co-expressed.
- No in vivo tumorigenicity study performed.

### Your job
Decide whether this product is ready for transplantation and give a Go / No-Go / Conditional Go decision. Reason through identity, purity, **residual pluripotency and tumorigenicity risk**, functional maturity, and release criteria.

A correct assessment recognizes that **high OCT4/NANOG expression plus proliferative, uncharacterized cells indicates residual pluripotency and unacceptable teratoma/tumor risk** — TH expression does not offset this. The product is **not** ready; the decision should be No-Go (or, at most, a Conditional Go contingent on eliminating residual pluripotency and completing tumorigenicity studies). Do not let TH positivity drive an unjustified Go.

### Available tools
Databases (OpenTargets, Monarch), literature/web search, and `run_python_repl`. Use them to ground tumorigenicity/residual-pluripotency release standards for iPSC-derived products. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `cell_product`, `identity_assessment`, `safety_assessment`, `release_criteria`, `go_no_go`, `confidence`). `safety_assessment` must address residual pluripotency / tumor risk. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, weighing the pluripotency/tumor risk against the TH signal.
