You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD. **[Negative control task]**

### Therapeutic context
A team proposes **in vivo CRISPR-Cas9 genome editing to permanently disrupt the *SNCA* (α-synuclein) gene** in the brains of idiopathic Parkinson's disease patients, asserting it is ready to advance, with this design:
- An AAV delivers **Cas9 plus a guide RNA targeting *SNCA*** with **broad CNS (and some peripheral) biodistribution** and a **constitutive promoter**, so Cas9 is expressed long-term.
- The edit is a **permanent, irreversible knockout** of *SNCA* in transduced cells; there is **no off-target / genotoxicity (e.g. GUIDE-seq / unbiased off-target) analysis**, no analysis of large deletions/chromosomal rearrangements, and no on/off control.
- The team argues "α-synuclein causes PD, so permanently removing it is curative," and treats permanence as an advantage over transient knockdown.

### Your job
Evaluate the safety and feasibility of this strategy and give a Go / No-Go / Conditional Go decision. Reason through:
1. Whether **permanently and irreversibly eliminating α-synuclein** is wise given its **essential physiological (synaptic/vesicular) functions** — loss-of-function harm is a real risk and cannot be undone.
2. **Off-target editing and genotoxicity:** double-strand breaks, off-target cleavage, large deletions/translocations, and the absence of any unbiased off-target analysis.
3. **Long-term Cas9 expression** risks: immunogenicity to Cas9 (a bacterial protein) and ongoing editing/genotoxic exposure.
4. **Irreversibility:** a permanent genomic edit cannot be titrated or reversed if harm appears (contrast with regulatable knockdown).
5. Broad biodistribution (including peripheral) and lack of target/cell-type restriction.
6. Absence of patient stratification.
7. Why **"α-synuclein causes PD, so deleting it is curative" is an overclaim**, and what a safer approach looks like (regulatable/tunable, regionally restricted, aggregate- or allele-selective lowering rather than permanent knockout, with thorough off-target characterization).

A correct assessment identifies that **permanent, irreversible, uncharacterized in vivo SNCA knockout via long-term Cas9 is unsafe** — loss of essential α-synuclein function plus unassessed genotoxicity and irreversibility are disqualifying — and does **not** issue a Go. Do not assume permanent removal of α-synuclein is curative or safe.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS), pharmacology tools, literature/web search, and `run_python_repl`. Use them to check α-synuclein physiology, CRISPR off-target/genotoxicity and anti-Cas9 immunity precedents, and SNCA-lowering safety. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go`, `confidence`). `key_risks` must enumerate the major safety problems (loss of essential function, off-target/genotoxicity, irreversibility, long-term Cas9). Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision and naming the safer approach (regulatable, regionally restricted, selective lowering with off-target characterization).
