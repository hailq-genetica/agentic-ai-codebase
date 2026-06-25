# PD-TxBench Expert Review Report — Gene-Therapy Family

**Tasks:** `gt_aav_gba1` (positive) + `gt_negative_snca_panbrain` (negative control)
**Family:** gene_therapy  ·  **Agent + judge:** `gpt-5.5-2026-04-23` (provider: openai)

> Packaged for **independent expert review**. The two tasks are a matched pair: the suite tests whether
> the agent both **advances** a credible AAV-GBA1 strategy (conditionally) and **rejects** an unsafe,
> non-specific SNCA-knockdown strategy. Automated LLM-judge scores (§A6/§B6) are a starting point, **not**
> the verdict — complete the worksheets in §A8/§B8/§C. Every factual claim and citation is **the agent's
> assertion, to be verified** (agent and judge are the same model — self-grading caveat applies).

---

## 0. Discrimination summary (read this first)

| | `gt_aav_gba1` (positive) | `gt_negative_snca_panbrain` (negative control) |
|---|---|---|
| Proposal | AAV-mediated *GBA1* gene addition for GBA-PD | non-specific, constitutive pan-brain *SNCA* shRNA knockdown |
| **Agent decision** | **Conditional Go** (conf 0.72) | **No-Go** (conf 0.94) |
| Gold decision | Conditional Go (Go acceptable) | No-Go (Conditional Go acceptable) |
| Decision match | ✅ match | ✅ match |
| Automated score | **1.0** (7/7 = 5) | **0.98** (6×5, biomarker 4) |
| Red flags | none | none |
| Effort | 60 tool calls, ~986k tok | 33 tool calls, ~364k tok |

**Discrimination is correct.** The agent advanced a mechanistically sound, genetically-stratified
AAV-GBA1 program *conditionally* — explicitly separating target-engagement rationale from unproven
clinical efficacy, and naming irreversibility, immunity, CNS-targeting gaps, and supraphysiologic-GCase
risk — while **rejecting** the pan-brain SNCA knockdown on the grounds that α-synuclein is an essential
synaptic protein, that high-expression AAV-shRNA carries a known fatal RNAi-saturation toxicity, and that
the design is irreversible and unstratified. Both decisions match gold; neither triggered a red flag.

---

# PART A — `gt_aav_gba1` (positive)

## A1. Provenance
Run `run_20260623_074624` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**59 steps / 60 tool calls (0 failures)** · ~986k tokens · judge `gpt-5.5-2026-04-23`.

## A2. Question
Critique an AAV-mediated *GBA1* delivery strategy for GBA-associated PD: genetic rationale, cargo/route,
CNS targeting, reversibility, immunity, overexpression risk, patient stratification, biomarkers,
preclinical models, clinical-translation challenges → Go/No-Go.

## A3. Agent decision
> **Conditional Go** · confidence **0.72** — "Mechanistically strong but not yet clinically proven disease modification."

## A4. Key reported content *(verify)*
- **Causal chain:** GBA1 LoF → ↑glucosylceramide/glucosylsphingosine + impaired lysosomal/autophagic
  degradation → α-synuclein accumulation, with α-synuclein further inhibiting GCase (feed-forward loop).
- **Why gene addition:** WT GBA1 cDNA avoids allele-specific correction; *but* doesn't remove mutant
  GBA1, may not reverse established Lewy pathology, and may need multi-region transduction.
- **Delivery:** intra-cisterna magna / intrathecal AAV9 (PR001/LY3884961 precedent); flags that human
  substantia nigra/putamen transduction is uncertain and DRG/peripheral exposure is a concern; notes
  **irreversibility / no post-dose titration** as a major weakness.
- **Stratification:** centrally-confirmed pathogenic GBA1 variants (distinguishing GBA1 from the **GBAP1
  pseudogene**), variant severity (N370S vs L444P), disease stage, baseline CSF GCase/GlcSph, anti-AAV9
  antibody status.
- **Biomarkers:** CSF GCase activity, GlcSph/GlcCer, α-synuclein seed-amplification/pS129, NfL, DaT/PET;
  clinical MDS-UPDRS II/III, MoCA, LEDD, safety MRI/spine/NCS.
- **Preclinical asks:** dose-ceiling in aged Gba1 mice + GBA1-mutant iPSC neurons/microglia; PFF/SNCA
  combination models; **NHP ICM biodistribution/tox**; potency assays; overexpression toxicity studies.
- **Key risks:** irreversibility, capsid/transgene immunity (incl. anti-GCase antibodies), CNS-targeting
  gap, supraphysiologic GCase, efficacy uncertainty if dosed too late, GBA1/GBAP1 genotyping complexity.

## A5. Citations to verify
| # | Source | Claim | ✓ |
|---|---|---|:--:|
| 1 | OpenTargets (MONDO_0005180) | GBA1 ranked ~12th for PD, association ~0.748 | ☐ |
| 2 | ClinicalTrials.gov **NCT04127578 (PROPEL)** | Ph1/2a ascending-dose LY3884961/PR001, single ICM dose, GBA-PD; safety/immunogenicity primary | ☐ |
| 3 | ClinicalTrials.gov NCT04411654 | PR001 ICM AAV-GBA1 in type 2 Gaucher infants (route precedent) | ☐ |
| 4 | UniProt P04062 | GBA1 = lysosomal GCase | ☐ |
| 5 | Sidransky et al., NEJM 2009 (PMID 19846850) | GBA–PD association, OR ~5.43 for any GBA mutation | ☐ |
| 6 | Mazzulli et al., Cell 2011 (PMID 21700325) | GCase loss → α-synuclein accumulation; bidirectional loop | ☐ |
| 7 | Okai et al., PLoS One 2025 (PMID 40333681) | AAV-GBA1 ↓GlcSph, ↓pS129/insoluble α-synuclein in models | ☐ |
| 8 | LeWitt et al., Lancet Neurol 2011 (PMID 21419704) | AAV2-GAD sham-controlled PD trial — CNS AAV precedent | ☐ |

> Verify each PMID/NCT exists and supports the stated claim (esp. the OR ~5.43 and the OpenTargets rank/score).

## A6. Automated judge (validate, don't trust)
Final **1.0**, all 7 criteria **5/5** (genetic rationale, delivery feasibility, safety, stratification,
biomarker/endpoint, validation plan, uncertainty). Judge: *"Excellent, expert-level … calibrated
Conditional Go … appropriately separates rationale/preclinical target engagement from demonstrated
clinical efficacy or long-term safety."*

## A7. Gold reference
Preferred **Conditional Go** (Go acceptable). Required concepts: GBA1, GCase, AAV delivery, CNS
targeting, overexpression risk, immune response, patient stratification, biomarkers, preclinical model.
Red flags: claims proven efficacy/safety; ignores overexpression; ignores immunity; ignores CNS
delivery; no stratification. *(Agent triggered none.)*

## A8. Expert worksheet — positive
- Citations 1–8 verified? ☐ all ✓ ☐ issues: __________
- Mechanism/loop, GBA1/GBAP1 caveat, ICM-AAV9 reasoning all correct? ☐ ✓ ☐ __________
- Per-criterion expert /5: genetic __ · delivery __ · safety __ · stratification __ · biomarker __ · validation __ · uncertainty __
- Agree with **Conditional Go**? ☐ Agree ☐ Disagree → __________ · Most important gap: __________
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

# PART B — `gt_negative_snca_panbrain` (negative control)

## B1. Provenance
Run `run_20260623_080415` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**32 steps / 33 tool calls (0 failures)** · ~364k tokens · judge `gpt-5.5-2026-04-23`.

## B2. Question
Evaluate the safety/feasibility of **non-specific, constitutive pan-brain SNCA knockdown** (ubiquitous-
promoter AAV-shRNA, no regional restriction, no dose titration) for idiopathic PD → Go/No-Go.

## B3. Agent decision
> **No-Go** · confidence **0.94**.

## B4. Key reported content *(verify)*
- **α-synuclein is essential, not disposable:** presynaptic vesicle trafficking, SNARE-complex assembly,
  neurotransmitter release — so broad suppression risks global synaptic loss-of-function toxicity. The
  agent explicitly notes knockout *viability in animals does not establish safety* of adult, widespread,
  partial-to-deep knockdown in humans.
- **shRNA platform toxicity:** high-expression AAV-shRNA can oversaturate endogenous miRNA/RNAi pathways
  — cites **Grimm 2006** lethal RNAi-saturation in mice — amplified by ubiquitous high-copy design.
- **Irreversibility / no dose control**, **pan-neuronal off-target + seed-mediated transcript
  off-targeting + innate immune activation**, and **no patient stratification**.
- **Safer redesign (constructive):** regional/cell-type-restricted delivery, tunable/reversible modality
  (dose-escalated ASO/siRNA with washout, regulatable cassette, amiRNA with expression caps), *partial
  normalization not pan-depletion*, biomarker stratification (seed-amplification / SNCA genetics), and
  allele-/aggregate-selective strategies sparing physiological monomeric α-synuclein.

## B5. Citations to verify
| # | Source | Claim | ✓ |
|---|---|---|:--:|
| 1 | UniProt P37840 | α-synuclein presynaptic vesicle-trafficking/exocytosis function | ☐ |
| 2 | OpenTargets ENSG00000145335 | SNCA association with Parkinsonian disorders + synaptic function | ☐ |
| 3 | Burré et al., Science 2010 | α-synuclein promotes SNARE-complex assembly | ☐ |
| 4 | Abeliovich et al., Neuron 2000 | α-synuclein-null mice: nigrostriatal DA deficits | ☐ |
| 5 | Cabin et al., J Neurosci 2002 | synaptic vesicle depletion / attenuated responses | ☐ |
| 6 | Grimm et al., Nature 2006 | fatal oversaturation of miRNA/shRNA pathways in mice | ☐ |

## B6. Automated judge (validate, don't trust)
Final **0.98**, criteria **5/5** except **biomarker_endpoint_selection 4/5**. Judge: *"Excellent,
well-calibrated … cites relevant biology and shRNA toxicity precedent, avoids the negative-control traps,
and proposes a realistic safer redesign. Minor limitation: biomarker/endpoint details could be more
specific."* — i.e. the only point dropped in the whole gene-therapy family is the agent under-specifying
pharmacodynamic biomarkers for the safer redesign; reviewer should confirm this is the right (minor) ding.

## B7. Gold reference
Preferred **No-Go** (Conditional Go acceptable). Red flags (should NOT occur): unqualified Go for
indiscriminate knockdown; assumes lowering α-synuclein is automatically safe; ignores α-synuclein
physiology; ignores shRNA/RNAi toxicity; ignores reversibility. *(Agent triggered none.)*

## B8. Expert worksheet — negative control
- Citations 1–6 verified (esp. Grimm 2006 RNAi-saturation; Burré 2010 SNARE)? ☐ all ✓ ☐ __________
- Did the agent correctly refuse to treat α-synuclein as a disposable target? ☐ ✓ ☐ __________
- Is the judge's biomarker 4/5 ding fair (vs the rest 5/5)? ☐ ✓ ☐ __________
- Per-criterion expert /5: genetic __ · delivery __ · safety __ · stratification __ · biomarker __ · validation __ · uncertainty __
- Agree with **No-Go**? ☐ Agree ☐ Disagree → __________
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

## C. Family-level expert judgment *(to complete)*
- **Discrimination correct?** Advanced AAV-GBA1 (conditionally) *and* rejected pan-brain SNCA knockdown
  for the right reasons? ☐ Yes ☐ Partially ☐ No — note: __________
- **Calibration:** Conditional-Go vs No-Go the right split (not both Go)? ☐ ✓ ☐ __________
- **Safety reasoning depth** (irreversibility, immunity, RNAi-saturation, supraphysiologic enzyme) adequate? ☐ ✓ ☐ __
- **Overall gene-therapy family grade (0–5): ___   Reviewer: ___   Date: ___   Specialty: ___**

## D. Audit pointers
- Deliverables: `…/gt_aav_gba1/run_20260623_074624/result.json`, `…/gt_negative_snca_panbrain/run_20260623_080415/result.json`
- Tool traces: the respective `agent.log` files · Methodology: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md` · Task defs: `docs/pdtx_task_definitions.md`
- Per-task auto-generated reports: `reports/pdtx/gt_aav_gba1_expert_review.md`, `reports/pdtx/gt_negative_snca_panbrain_expert_review.md`
