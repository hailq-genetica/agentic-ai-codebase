You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of a PD cell-therapy product. **[Negative control task]**

### Therapeutic context
A protocol generates **iPSC-derived midbrain dopaminergic (mDA) neurons** intended for **putaminal transplantation in Parkinson's disease**, with an otherwise encouraging identity profile but a genomic-integrity problem revealed at expansion:
- Dopaminergic identity (TH, NURR1, PITX3) and midbrain floor-plate lineage (FOXA2, LMX1A) expressed in the majority of cells.
- Residual pluripotency markers (OCT4, NANOG) **below detection**, and functional dopamine release demonstrated in vitro.
- **BUT** genomic QC on the expanded working bank shows: a **recurrent karyotype abnormality** (a culture-acquired **chromosome 20q11.21 copy-number gain** plus a **chromosome 12p gain**, both recurrently selected in pluripotent-stem-cell culture), and targeted sequencing detected an **acquired dominant-negative TP53 mutation** in a subclone.
- **No in vivo tumorigenicity study** has been performed.

### Your job
Decide whether this product is ready for transplantation and give a Go / No-Go / Conditional Go decision. Reason through identity, **genomic integrity / genomic instability**, tumorigenicity risk, and release criteria.

A correct assessment recognizes that **genomic instability is an independent transformation / tumorigenicity risk that is not detected by pluripotency markers** — undetectable OCT4/NANOG and good DA identity do **not** offset a culture-acquired oncogenic karyotype/mutation. The 20q11.21 gain (which amplifies the anti-apoptotic gene *BCL2L1*), the 12p gain, and especially the **acquired TP53 mutation** confer selective growth advantage and elevated tumorigenic/transformation potential, and there is no in vivo tumor study. The decision should be **No-Go** (at most a Conditional Go contingent on re-deriving a genomically stable line, adding genomic-integrity release criteria — karyotype, CNV/SNP array, driver-gene sequencing — and completing in vivo tumorigenicity studies). Do not let clean pluripotency QC or good DA identity drive an unjustified Go.

### Available tools
Databases (OpenTargets, Monarch, ClinVar), literature/web search, and `run_python_repl`. Use them to ground recurrent PSC genomic abnormalities (e.g. 20q11.21 / BCL2L1, 12p), the significance of acquired TP53 mutations, and genomic-integrity release standards for iPSC-derived products. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `cell_product`, `identity_assessment`, `safety_assessment`, `release_criteria`, `go_no_go`, `confidence`). `safety_assessment` must address genomic instability / tumorigenicity independent of pluripotency markers. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, weighing the genomic instability and absent in vivo tumor data against the good identity and clean pluripotency QC.
