# PD-TxBench Expert Review Report — gt_negative_snca_panbrain

**Task:** `gt_negative_snca_panbrain`  ·  **Family:** gene_therapy  ·  **Type:** negative control

> Packaged for **independent expert review**. The automated LLM-judge score (§5) is a starting point, not the verdict — complete the worksheet in §7. Treat every factual claim and citation below as **the agent's assertion, to be verified**.

## 1. Provenance

| Field | Value |
|---|---|
| Run | `run_20260623_080415` |
| Agent model | `gpt-5.5-2026-04-23` (provider: openai) |
| Reasoning effort | high |
| Mode | autonomous |
| Steps / tools loaded | 32 steps, 82 tools (failures: 0) |
| Tokens | 363,656 |
| Judge | `gpt-5.5-2026-04-23` (provider: openai) |
| Artifacts | `output/pdtx/gene_therapy/gt_negative_snca_panbrain/run_20260623_080415/` (result.json, reasoning.txt, agent.log, verification_notebook.ipynb) |

## 2. Question posed

See the full task prompt at `tasks/pdtx/gene_therapy/gt_negative_snca_panbrain.md`. The agent had to work the full therapeutic-reasoning chain and return a decision.

## 3. Agent's decision

> **Decision: No-Go**  ·  **Confidence: 0.94**

## 4. Agent's deliverable (full structured output)

- **therapeutic_rationale**:
  - **summary**: Lowering SNCA/alpha-synuclein is biologically plausible for synucleinopathy because SNCA gain-of-function, duplication/triplication and Lewy pathology implicate alpha-synuclein in PD. However, the proposed modality is indiscriminate total/pathway suppression, not a disease-selective normalization strategy.
  - **evidence_checked**:
    - UniProtKB P37840: alpha-synuclein is a neuronal presynaptic protein involved in synaptic vesicle trafficking, vesicle exocytosis and neurotransmitter release.
    - OpenTargets ENSG00000145335: SNCA is genetically/biologically associated with Parkinsonian disorders and has annotated synaptic function.
    - PubMed: Burre et al., 'Alpha-synuclein promotes SNARE-complex assembly in vivo and in vitro' (Science 2010).
    - PubMed: Abeliovich et al., 'Mice lacking alpha-synuclein display functional deficits in the nigrostriatal dopamine system' (Neuron 2000).
    - PubMed: Cabin et al., 'Synaptic vesicle depletion correlates with attenuated synaptic responses...' (J Neurosci 2002).
    - PubMed: Grimm et al., 'Fatality in mice due to oversaturation of cellular microRNA/short hairpin RNA pathways' (Nature 2006).
  - **interpretation**: The disease rationale does not override the need to preserve physiological alpha-synuclein and endogenous miRNA/RNAi capacity. Broad constitutive knockdown risks converting a gain-of-toxic-function concept into global loss-of-function synaptic toxicity.
- **delivery_strategy**:
  - **proposed**: Broadly biodistributed AAV encoding an anti-SNCA shRNA from a constitutive/ubiquitous promoter, with no regional targeting, patient selection, reversibility or dose titration.
  - **assessment**: Not feasible for clinical development as specified. Exposure would be heterogeneous yet long-lasting across vulnerable and non-vulnerable brain regions, and shRNA expression level would be difficult to control after administration.
  - **safer_redesign_required**:
    - Restrict expression to disease-relevant circuits/regions (e.g., MRI-guided putaminal/nigrostriatal delivery rather than pan-brain biodistribution) and consider cell-type-specific or weaker Pol-II promoters.
    - Use a tunable/regulatable or reversible modality: dose-escalated ASO/siRNA with washout, regulatable AAV cassette, or miRNA-embedded/amiRNA design with expression caps rather than high-copy constitutive shRNA.
    - Aim for partial normalization, not near-complete pan-neuronal depletion, with pharmacodynamic biomarkers of SNCA lowering and synaptic safety readouts.
    - Stratify patients by synuclein pathology/SNCA genetics or seed-amplification biomarkers, and exclude patients unlikely to benefit.
    - Prefer allele-selective approaches for SNCA mutations/multiplications when possible, or aggregate-/seed-selective clearance strategies that spare physiological monomeric alpha-synuclein.
- **key_risks**:
  -
    - **risk**: Physiological alpha-synuclein loss-of-function
    - **severity**: High
    - **details**: Alpha-synuclein participates in presynaptic vesicle trafficking, vesicle exocytosis, SNARE-complex assembly and neurotransmitter release. Pan-brain constitutive suppression may impair dopaminergic and non-dopaminergic synaptic function, cognition, autonomic circuits and motor networks. Knockout viability in animals does not establish safety of adult, widespread, partial-to-deep knockdown in humans.
  -
    - **risk**: Pan-neuronal/off-target consequences of broad AAV and shRNA expression
    - **severity**: High
    - **details**: A ubiquitous construct would expose non-diseased regions and multiple neuronal/glial populations. shRNAs can produce seed-mediated transcript off-targeting, innate immune activation and transcriptome-wide perturbation independent of SNCA lowering.
  -
    - **risk**: Irreversibility and lack of dose control
    - **severity**: High
    - **details**: AAV genomes can persist for years. Constitutive promoter-driven shRNA cannot be readily stopped, titrated downward, or spatially adjusted after administration; heterogeneous vector biodistribution makes safe exposure margins hard to define.
  -
    - **risk**: Known toxicity of high-expression AAV shRNA
    - **severity**: High
    - **details**: AAV-delivered shRNA can oversaturate endogenous miRNA/RNAi processing/export/RISC pathways; Grimm et al. reported lethal toxicity in mice from RNAi pathway oversaturation. This is a platform risk amplified by ubiquitous, high-expression designs.
  -
    - **risk**: No patient stratification
    - **severity**: Moderate-to-High
    - **details**: Idiopathic PD is heterogeneous. Without evidence of active synuclein pathology, SNCA dosage/pathogenic variants, or biomarker-defined target engagement potential, many patients could receive irreversible pan-brain knockdown with uncertain benefit.
  -
    - **risk**: Clinical translational feasibility
    - **severity**: High
    - **details**: Therapeutic window is likely narrow: sufficient lowering to affect pathology may overlap with synaptic toxicity; pan-brain delivery also complicates biodistribution, immunogenicity, manufacturing dose, and safety monitoring.
- **go_no_go**: No-Go
- **confidence**: 0.94

### Agent reasoning narrative (`reasoning.txt`)

> Decision: No-Go for the proposed non-specific constitutive pan-brain SNCA knockdown. The target is not a disposable toxic protein: UniProt P37840 and OpenTargets annotate alpha-synuclein as a presynaptic neuronal protein regulating synaptic vesicle trafficking/exocytosis and neurotransmitter release; PubMed-cited work shows roles in SNARE-complex assembly (Burre et al., Science 2010) and nigrostriatal/synaptic phenotypes in alpha-synuclein-deficient mice (Abeliovich et al., Neuron 2000; Cabin et al., J Neurosci 2002). A ubiquitous AAV-shRNA would expose healthy cortical, limbic, autonomic and cerebellar circuits to long-lived knockdown plus shRNA seed off-targets/immune effects. Constitutive AAV expression is poorly reversible and hard to titrate after dosing. High shRNA expression has a known class toxicity: oversaturation of endogenous miRNA/RNAi pathways caused severe/fatal toxicity in mice (Grimm et al., Nature 2006). The proposal also lacks biomarker or genetic stratification. A viable redesign would require regional/cell-type targeting, partial/tunable or reversible expression, capped miRNA/ASO-like chemistry, and allele- or aggregate-selective strategies with patient stratification.

## 5. Evidence base and methods (audit trail)

**Methodology:** 32 steps — tool use: run_python_repl ×13, query_pubmed ×12, query_uniprot ×3, query_opentarget ×2, advanced_web_search_claude ×1, search_google ×1.

Representative search queries:
- `alpha-synuclein synaptic vesicle trafficking neurotransmitter release physiological function review`
- `alpha-synuclein promotes SNARE complex assembly neurotransmitter release Burre Sharma Sudhof 2010 Science`
- `alpha-synuclein knockout mice synaptic dysfunction dopamine neurotransmission essential physiology`
- `AAV shRNA toxicity saturation microRNA pathway neuronal liver Grimm Kay 2006 Nature snca Parkinson gene therapy shRNA safety`
- `Grimm fatality mice shRNA saturation endogenous microRNA pathway AAV Nature 2006`
- `Grimm et al 2006 Nature AAV shRNA toxicity saturation endogenous RNAi microRNA pathway fatality mice`
- `Grimm 2006 Nature AAV shRNA toxicity saturation endogenous RNAi pathway`
- `Fatality in mice due to oversaturation of cellular microRNA short hairpin RNA pathway Nature 2006`
- `AAV shRNA brain toxicity RNAi saturation neurons basal ganglia Parkinson alpha synuclein knockdown`
- `short hairpin RNA toxicity brain AAV neurons endogenous microRNA saturation`
- `alpha synuclein knockdown antisense oligonucleotide safety physiological reduction Parkinson's disease neurons review`
- `targeting alpha-synuclein lowering therapy Parkinson disease safety physiological function presynaptic protein review`

**Citations the agent relied on — verify each supports the stated claim:**

_No structured `evidence_used` field in the deliverable; check `reasoning.txt` and `agent.log` for cited sources._

> The most common LLM failure mode is a plausible-but-wrong citation: confirm each PMID/DOI exists, matches title/author/year, and supports the claim.

## 5b. Automated evaluation (LLM-as-judge) — validate, don't trust

Judge `gpt-5.5-2026-04-23`, rubric `pdtx_gene_therapy_eval_v1`. **Final score 0.98**, decision_match = **match** (gold = No-Go), schema-valid: True, red flags: none.

| Criterion | Score /5 | Judge justification (abridged) |
|---|:--:|---|
| genetic_rationale | 5 | Clearly distinguishes the plausible disease rationale for SNCA lowering (genetic dosage, Lewy pathology) from the unsafe assumption that broad suppression is beneficial,  |
| delivery_feasibility | 5 | Directly identifies broad biodistribution, ubiquitous/constitutive expression, heterogeneous long-lasting exposure, and lack of regional targeting as major feasibility ba |
| safety_risk_analysis | 5 | Comprehensively covers alpha-synuclein synaptic/vesicular functions, pan-neuronal off-target effects, irreversibility/dose-control problems, and high-expression AAV-shRNA |
| patient_stratification | 5 | Explicitly flags idiopathic PD heterogeneity and absence of biomarker/genetic stratification, and proposes stratification by synuclein pathology, SNCA genetics, or seed-a |
| biomarker_endpoint_selection | 4 | Mentions pharmacodynamic biomarkers of SNCA lowering, synaptic safety readouts, synuclein pathology/seed-amplification biomarkers, and target engagement. It is strong but |
| validation_plan | 5 | Provides an actionable safer redesign: regional/circuit targeting, cell-type-specific or weaker promoters, tunable/reversible modalities, miRNA-embedded designs, partial  |
| uncertainty_handling | 5 | Issues a clear No-Go for the proposed strategy, avoids overclaiming benefit, and explicitly notes animal knockout viability does not prove human safety. |

> ⚠️ **Self-grading caveat:** agent and judge are the same provider/model — risk of self-consistency bias. The expert score (§7) is authoritative; cross-provider judging (`--judge-provider`) can reduce this.

## 6. Gold reference (calibration)

- **Preferred decision:** No-Go (acceptable: ['Conditional Go'])
- **Required concepts:** alpha-synuclein physiological function, pan-brain / non-specific suppression risk, lack of reversibility / dose control, shRNA toxicity / RNAi saturation, no patient stratification, safer redesign (regional / regulatable)
- **Red flags (should NOT occur):** issues an unqualified Go for indiscriminate SNCA knockdown; assumes lowering alpha-synuclein is automatically safe; ignores essential physiological role of alpha-synuclein; ignores shRNA / RNAi-saturation toxicity; ignores lack of reversibility and dose control
- **Gold rationale:** Non-specific, constitutive pan-brain SNCA knockdown is unsafe and infeasible as proposed: alpha-synuclein has essential synaptic functions, broad suppression risks neuronal toxicity, constitutive shRNA lacks reversibility/dose control and can saturate endogenous RNAi machinery (known AAV-shRNA neurotoxicity), and there is no patient stratification. The correct decision is No-Go; a safer redesign requires regional targeting, regulatable/tunable expression, and aggregate/allele selectivity.

## 7. Expert review worksheet *(to complete)*

**A. Factual accuracy / hallucination check**
- Citations verified (exist + support claim)? ☐ all ✓  ☐ issues: ____________________
- Domain facts correct (mechanism, markers, trials, numbers)? ☐ ✓  ☐ ____________________
- Any fabricated sources/assays/data? ☐ none  ☐ ____________________

**B. Per-criterion expert score (0–5)** — override the automated scores
| Criterion | Expert /5 | Note |
|---|:--:|---|
| genetic_rationale | ☐ | |
| delivery_feasibility | ☐ | |
| safety_risk_analysis | ☐ | |
| patient_stratification | ☐ | |
| biomarker_endpoint_selection | ☐ | |
| validation_plan | ☐ | |
| uncertainty_handling | ☐ | |

**C. Decision** — agree with **No-Go**? ☐ Agree ☐ Disagree → your call: ____________
**D. Most important omission or error (if any):** ____________________
**E. Trust as a first-pass assessment?** ☐ Yes ☐ With edits ☐ No
**F. Overall expert grade (0–5): ____  Reviewer: ______  Date: ______  Specialty: ______**

## 8. Audit pointers
- Structured output: `output/pdtx/gene_therapy/gt_negative_snca_panbrain/run_20260623_080415/result.json`
- Tool-by-tool trace: `output/pdtx/gene_therapy/gt_negative_snca_panbrain/run_20260623_080415/agent.log`
- Methodology & scoring: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md`
- Task definition: `docs/pdtx_task_definitions.md` → `gt_negative_snca_panbrain`
