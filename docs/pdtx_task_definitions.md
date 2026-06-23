# PD-TxBench — Evaluation Task Definitions

Reference for the PD-TxBench evaluation tasks: what each one presents to the agent, what it tests, and
the gold decision it is scored against. For methodology see
[`pdtx_agentic_evaluation.md`](pdtx_agentic_evaluation.md); for scoring mechanics see
[`pdtx_scoring_guide.md`](pdtx_scoring_guide.md). Task prompts live in `tasks/pdtx/<family>/<id>.md`,
gold/rubric files in `tasks/pdtx/gold/<id>.json`, configs in `config/pdtx/<family>/<id>.yaml`.

## Design principles

1. **Cover the three therapy modalities** the program cares about — small molecule, gene therapy, cell
   therapy — plus an evidence-appraisal family that tests claim verification directly.
2. **Each task is decision-bearing.** The agent must reach a Go / No-Go / Conditional Go (or a claim
   classification), not just describe biology.
3. **Pair every positive with a negative control.** For each family there is a case that *should*
   progress and one that *should not*. The negative controls are the point: a fluent model can
   rationalize almost anything, so the benchmark measures whether the agent can correctly say
   **No-Go / Contradicted** when the evidence demands it.
4. **Reward honest uncertainty.** Gold answers distinguish mechanistic plausibility and biomarker /
   target-engagement signals from *proven* clinical efficacy; overclaiming is an explicit red flag.

## Task index

| ID | Family | Type | Gold decision | Tests |
|---|---|---|---|---|
| `sm_gba1_ambroxol_analog` | small_molecule | positive | Conditional Go | GCase-chaperone candidate evaluation for GBA1-PD |
| `sm_negative_herg_bbb` | small_molecule | negative | No-Go | good docking ≠ developable (BBB + hERG kill it) |
| `gt_aav_gba1` | gene_therapy | positive | Conditional Go | AAV gene-addition strategy critique |
| `gt_negative_snca_panbrain` | gene_therapy | negative | No-Go | unsafe, non-specific knockdown strategy |
| `ct_ipsc_da_neurons` | cell_therapy | positive | Conditional Go | iPSC-DA-neuron translational readiness |
| `ct_negative_residual_pluripotency` | cell_therapy | negative | No-Go | residual pluripotency → tumor risk |
| `ev_ambroxol_dmt_claim` | evidence_reasoning | positive | Partially supported | claim verification with mixed evidence |
| `ev_negative_mouse_to_clinical` | evidence_reasoning | negative | Contradicted | preclinical→clinical overclaim |

Decision vocabulary: therapy families use **Go / No-Go / Conditional Go**; evidence_reasoning uses
**Supported / Partially supported / Unsupported / Contradicted**.

---

## Small molecule

Rubric weights (`pdtx_sm_candidate_eval_v1`): PD mechanism 0.20 · target/MoA 0.15 · ADMET 0.20 ·
safety risk 0.15 · Go/No-Go quality 0.15 · next experiment 0.10 · uncertainty 0.05.

### `sm_gba1_ambroxol_analog` — positive — Conditional Go (Go acceptable)
- **Scenario:** evaluate "Ambroxol analog A" (a GCase pharmacological chaperone) as a therapeutic for
  GBA1-associated PD, given its SMILES and proposed target (GCase).
- **Tests:** the full candidate-evaluation chain — disease relevance (GBA1→GCase→lysosome→α-synuclein),
  chaperone MoA plausibility, BBB penetration for a CNS target, ADMET/safety (solubility, clearance,
  CYP, hERG, AMES, DILI), patent/novelty, and a calibrated decision + next experiment.
- **Required concepts:** GCase, GBA1, lysosomal, α-synuclein, pharmacological chaperone, blood-brain
  barrier, ADMET, safety liability, next experiment.
- **Red flags:** claims proven disease modification; ignores BBB/CNS penetration; ignores ADMET/safety;
  treats docking/binding as proof of efficacy.
- **Note:** the SMILES is in fact ambroxol itself — a strong agent recognizes this (dominating the
  novelty/IP verdict) rather than treating it as a novel analog.

### `sm_negative_herg_bbb` — negative control — No-Go (Conditional Go acceptable)
- **Scenario:** "Compound X" has strong predicted GCase binding **but** poor BBB penetration and a
  strong hERG liability.
- **Tests:** whether the agent recognizes that target affinity does not rescue a molecule that cannot
  reach the CNS and carries a serious cardiac liability — i.e. distinguishes mechanistic appeal from
  developability.
- **Red flags:** issues a Go driven by docking despite the liabilities; ignores BBB; ignores hERG;
  treats strong binding as sufficient to progress.

---

## Gene therapy

Rubric weights (`pdtx_gene_therapy_eval_v1`): genetic rationale 0.20 · delivery feasibility 0.15 ·
safety risk 0.20 · patient stratification 0.15 · biomarker/endpoint 0.10 · validation plan 0.15 ·
uncertainty 0.05.

### `gt_aav_gba1` — positive — Conditional Go (Go acceptable)
- **Scenario:** critique a proposal for AAV-mediated *GBA1* delivery to restore GCase in GBA-associated PD.
- **Tests:** genetic rationale, cargo/route and CNS targeting (serotype/tropism), reversibility/dose
  control, capsid/transgene immunity, **GCase overexpression risk**, patient stratification (GBA1
  carriers), biomarkers (GCase activity, glucosylceramide), preclinical models, clinical-translation
  challenges.
- **Required concepts:** GBA1, GCase, AAV delivery, CNS targeting, overexpression risk, immune response,
  patient stratification, biomarkers, preclinical model.
- **Red flags:** claims proven efficacy/safety; ignores overexpression/dose-control; ignores
  capsid/transgene immunity; ignores CNS delivery/biodistribution; no patient stratification.

### `gt_negative_snca_panbrain` — negative control — No-Go (Conditional Go acceptable)
- **Scenario:** non-specific, constitutive knockdown of *SNCA* across **all** brain regions (ubiquitous
  promoter, no regional restriction, no dose titration) for idiopathic PD.
- **Tests:** whether the agent identifies the major safety problems — α-synuclein's essential synaptic
  functions, pan-neuronal toxicity, lack of reversibility/dose control, AAV-shRNA RNAi-saturation
  toxicity, absent stratification — and proposes a safer redesign (regional, regulatable, allele/aggregate
  selective) rather than issuing an unqualified Go.
- **Red flags:** unqualified Go for indiscriminate knockdown; assumes lowering α-synuclein is
  automatically safe; ignores α-synuclein physiology; ignores shRNA/RNAi toxicity; ignores reversibility.

---

## Cell therapy

Rubric weights (`pdtx_cell_therapy_eval_v1`): cell identity 0.20 · safety/tumorigenicity 0.20 ·
functional maturity 0.15 · manufacturing/reproducibility 0.15 · release criteria 0.15 · translational
decision 0.10 · uncertainty 0.05.

### `ct_ipsc_da_neurons` — positive — Conditional Go (Go acceptable)
- **Scenario:** judge the translational readiness of iPSC-derived midbrain dopaminergic (mDA) neurons
  for PD transplantation, given a QC profile: TH/NURR1/PITX3 in most cells, FOXA2/LMX1A floor-plate
  markers, undetectable residual pluripotency, demonstrated dopamine release.
- **Tests:** DA/midbrain (A9) identity, purity, residual pluripotency / tumorigenicity, functional
  maturity, graft survival/integration, batch reproducibility, potency assays, release criteria — and
  the recognition that encouraging characterization is *necessary but not sufficient* (in vivo
  engraftment + tumorigenicity studies still required).
- **Required concepts:** dopaminergic identity (TH/NURR1/PITX3), midbrain floor-plate (FOXA2/LMX1A),
  residual pluripotency/tumorigenicity, functional dopamine release, graft survival, release criteria,
  batch reproducibility.
- **Red flags:** declares clinically ready without in vivo/tumorigenicity data; ignores residual
  pluripotency; ignores graft survival or potency/release criteria.

### `ct_negative_residual_pluripotency` — negative control — No-Go (Conditional Go acceptable)
- **Scenario:** a product expresses TH in many cells **but** shows high residual OCT4/NANOG, a
  proliferative (Ki-67+) fraction, only partial floor-plate co-expression, and no in vivo tumorigenicity
  study.
- **Tests:** whether the agent recognizes that residual pluripotency + uncharacterized proliferative
  cells = unacceptable teratoma/tumor risk, and that TH positivity does not offset it → No-Go.
- **Red flags:** Go despite high OCT4/NANOG and tumor risk; treats TH positivity as sufficient; ignores
  residual pluripotency/tumorigenicity; ignores absent in vivo tumorigenicity study.

---

## Evidence reasoning

Rubric weights (`pdtx_evidence_verification_v1`): correct classification 0.30 · evidence use 0.25 ·
preclinical-vs-clinical 0.20 · uncertainty 0.15 · avoids overclaiming 0.10.

### `ev_ambroxol_dmt_claim` — positive — Partially supported
- **Scenario:** classify the claim *"Ambroxol is a disease-modifying therapy for Parkinson's disease."*
- **Tests:** whether the agent retrieves the real evidence (mechanistic GCase-chaperone rationale; the
  open-label AiM-PD proof-of-concept; the more recent placebo-controlled trial that missed its primary
  endpoint) and lands on **Partially supported** — genuine plausibility and biomarker/target-engagement
  signal, but disease modification not established. Neither overclaim ("Supported") nor dismiss
  ("Unsupported").
- **Red flags:** classifies Supported/proven DMT; classifies Unsupported (denies any rationale); fails
  to separate preclinical/biomarker evidence from clinical efficacy; overstates trial strength.

### `ev_negative_mouse_to_clinical` — negative control — Contradicted (Unsupported acceptable)
- **Scenario:** a single 6-OHDA mouse motor-behavior improvement is asserted as *proof* of clinical
  efficacy in PD patients.
- **Tests:** whether the agent recognizes this as preclinical-only evidence, articulates the
  translational gap (no human PK/safety/efficacy), and rejects the inference as **overclaiming**, stating
  what human evidence would actually be required.
- **Red flags:** endorses the mouse→clinical "proof"; classifies Supported/Partially supported; fails to
  identify the overclaim; treats animal motor improvement as clinical proof.

---

## Output contract per family

Each `result.json` must satisfy the per-category definition in
`tasks/pdtx/schemas/output_schema_v2.json` (structural contract: required keys + valid decision enum +
0–1 confidence):

| Family | Required keys |
|---|---|
| small_molecule | `mechanism_hypothesis`, `admet_assessment`, `go_no_go`, `main_risks`, `next_experiment`, `confidence` |
| gene_therapy | `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go`, `confidence` |
| cell_therapy | `cell_product`, `identity_assessment`, `safety_assessment`, `release_criteria`, `go_no_go`, `confidence` |
| evidence_reasoning | `classification`, `rationale`, `confidence` |

## Adding tasks

To add a task: create `tasks/pdtx/<family>/<id>.md` (prompt + deliverable instructions),
`tasks/pdtx/gold/<id>.json` (decision, required_concepts, acceptable_variants, red_flags, weighted
rubric summing to 1.0), and `config/pdtx/<family>/<id>.yaml`. No code changes needed — `run_pdtx.py`
discovers configs by directory. Keep the positive/negative-control pairing and an explicit gold decision.
