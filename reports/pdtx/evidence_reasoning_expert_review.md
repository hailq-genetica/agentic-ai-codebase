# PD-TxBench Expert Review Report — Evidence-Reasoning Family

**Tasks:** `ev_ambroxol_dmt_claim` (positive) + `ev_negative_mouse_to_clinical` (negative control)
**Family:** evidence_reasoning  ·  **Agent + judge:** `gpt-5.5-2026-04-23` (provider: openai)

> Packaged for **independent expert review**. This family tests **claim verification** — can the agent
> grade a therapeutic claim against the real evidence base, distinguish mechanistic/biomarker signal from
> proven clinical efficacy, and *refuse to overclaim*? The two tasks are a matched pair: a genuinely
> mixed-evidence claim (should be **Partially supported**) and a preclinical→clinical overreach (should be
> **Contradicted**). Automated LLM-judge scores (§A6/§B6) are a starting point, **not** the verdict —
> complete the worksheets. Every cited paper/PMID/NCT is **the agent's assertion, to be verified**
> (agent and judge are the same model — self-grading caveat applies).

---

## 0. Discrimination summary (read this first)

| | `ev_ambroxol_dmt_claim` (positive) | `ev_negative_mouse_to_clinical` (negative control) |
|---|---|---|
| Claim graded | "Ambroxol is a disease-modifying therapy for PD." | "Mouse 6-OHDA motor improvement ⇒ proven clinically effective." |
| **Agent classification** | **Partially supported** (conf 0.84) | **Contradicted** (conf 0.96) |
| Gold | Partially supported | Contradicted (Unsupported acceptable) |
| Decision match | ✅ match | ✅ match |
| Automated score | **1.0** (5/5 all) | **1.0** (5/5 all) |
| Red flags | none | none |
| Effort | 99 tool calls, ~1.78M tok | 22 tool calls, ~154k tok |

**Discrimination is correct and is the whole point of this family.** The agent neither *over*-credited
ambroxol (it did **not** say "Supported") nor *dismissed* it ("Unsupported") — landing on the nuanced
**Partially supported** with the key separation: real mechanism + biomarker target engagement, but the
**only adequately controlled trial (2025 PDD RCT) missed its endpoints**, so disease modification is
unproven. On the negative control it **rejected the overclaim** outright (Contradicted), correctly
demoting a single toxin-model result to hypothesis-generating evidence and even running a
ClinicalTrials.gov query that returned no "Compound Q" PD trials. No overclaiming red flags in either.

---

# PART A — `ev_ambroxol_dmt_claim` (positive)

## A1. Provenance
Run `run_20260623_081637` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**98 steps / 99 tool calls (1 handled failure)** · ~1.78M tokens · judge `gpt-5.5-2026-04-23`.

## A2. Claim graded
"Ambroxol is a disease-modifying therapy for Parkinson's disease." → classify
Supported / Partially supported / Unsupported / Contradicted.

## A3. Agent classification
> **Partially supported** · confidence **0.84**.

## A4. Key reported content *(verify)*
- **Mechanism:** ambroxol = GCase (GBA1) pharmacological chaperone; restoring lysosomal GCase →
  improved autophagy + reduced α-synuclein; strongest rationale in GBA-PD.
- **Preclinical:** McNeill 2014 (↑glucosylceramidase in patient/GBA-carrier fibroblasts);
  Migdalska-Richards 2016 (↑brain GCase + ↓α-syn/pS129 in transgenic mice).
- **Clinical (the decisive part):**
  - **Mullin 2020 (JAMA Neurol, NCT02941822):** open-label, **non-controlled**, n=23/18; CSF penetration,
    ↑CSF GCase (35%) and α-syn (13%), MDS-UPDRS III improved — but no placebo, biomarker/PD endpoint.
  - **Athauda 2025 (JAMA Neurol, NCT02914366):** **52-wk double-blind placebo-controlled PDD RCT**, n=55;
    safe + GCase target engagement but **no benefit on primary/secondary cognitive/clinical outcomes**.
  - **AMBITIOUS (NCT05287503)** completed, no posted results; **ASPro-PD ph3 (NCT05778617)** + **GREAT
    (NCT05830396)** pending.
- **Interpretation:** mechanistic plausibility + biomarker engagement ≠ demonstrated disease
  modification; to upgrade, need adequately-powered RCT(s) showing slowed progression with durability.

## A5. Citations to verify
| # | Source | Claim | ✓ |
|---|---|---|:--:|
| 1 | Sidransky et al., NEJM 2009 (PMID 19846850) | GBA–PD association, OR ~5.4 | ☐ |
| 2 | McNeill et al., Brain 2014 (PMID 24574503) | ambroxol ↑GCase in GBA-carrier PD cells | ☐ |
| 3 | Migdalska-Richards et al., Ann Neurol 2016 (PMID 27859541) | ↑brain GCase, ↓α-syn in transgenic mice | ☐ |
| 4 | Mullin et al., JAMA Neurol 2020 (PMID 31930374, NCT02941822) | open-label PoC: CSF penetration/biomarkers, not controlled | ☐ |
| 5 | Athauda et al., JAMA Neurol 2025 (PMID 40587145, NCT02914366) | 52-wk PDD RCT: target engagement, **no cognitive benefit** | ☐ |
| 6 | NCT05287503 / NCT05778617 / NCT05830396 | AMBITIOUS completed (no results) / ASPro-PD ph3 / GREAT pending | ☐ |

> Highest-value checks: (a) does Athauda 2025 really exist and report a **negative** primary endpoint
> (this is load-bearing for "Partially supported" vs "Supported")? (b) Mullin 2020 numbers (35%/13%).

## A6. Automated judge (validate, don't trust)
Final **1.0**, all 5 criteria **5/5** (classification, evidence use, preclinical-vs-clinical, uncertainty,
avoids overclaiming). Judge: *"Excellent, well-calibrated … distinguishes biomarkers from proven clinical
benefit, and states what evidence is needed for disease-modification claims."*

## A7. Gold reference
Preferred **Partially supported**. Required concepts: GCase chaperone mechanism, GBA-PD, early-phase
evidence, biomarker vs clinical outcome, not conclusively disease-modifying, plausibility ≠ proven
efficacy. Red flags: classifies Supported/proven DMT; classifies Unsupported; fails to separate
preclinical/biomarker from clinical; overstates trial strength. *(Agent triggered none.)*

## A8. Expert worksheet — positive
- Citations 1–6 verified (esp. Athauda 2025 negative result; Mullin 2020 figures)? ☐ all ✓ ☐ __________
- Is **Partially supported** the right call (not Supported, not Unsupported)? ☐ ✓ ☐ → __________
- Per-criterion expert /5: classification __ · evidence use __ · preclinical-vs-clinical __ · uncertainty __ · avoids-overclaiming __
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

# PART B — `ev_negative_mouse_to_clinical` (negative control)

## B1. Provenance
Run `run_20260623_083912` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**21 steps / 22 tool calls (0 failures)** · ~154k tokens · judge `gpt-5.5-2026-04-23`.

## B2. Claim graded
"A 6-OHDA mouse motor-behavior improvement after Compound Q ⇒ Compound Q is **proven** clinically
effective for PD patients." → classify.

## B3. Agent classification
> **Contradicted** · confidence **0.96**.

## B4. Key reported content *(verify)*
- **Names the logical leap explicitly:** "Overclaiming: 'worked in one mouse toxin-model behavioral
  assay' → 'proven clinically effective' without human efficacy or benefit-risk evidence."
- **Demotes the evidence:** a single 6-OHDA result is preclinical/hypothesis-generating; the model
  captures dopaminergic toxin injury + motor deficits, *not* the chronic heterogeneous human disease,
  Lewy/α-syn pathology, non-motor features, placebo effects, or safety constraints; rotarod gains may be
  symptomatic/nonspecific.
- **Did the verification work:** ran a **ClinicalTrials.gov v2 query** for "Compound Q" + Parkinson →
  **no studies** (confirmed absence of human data), and pulled a review on neurotoxin-model limitations.
- **States what would be required:** replication + PD target engagement/dose-response; ADME/PK + BBB +
  GLP tox; phase 1 human safety/PK; adequately-powered RCT(s) with prespecified MDS-UPDRS endpoints.

## B5. Citations to verify
| # | Source | Claim | ✓ |
|---|---|---|:--:|
| 1 | Provided prompt evidence | one 6-OHDA rodent study, rotarod improvement; no human data | ☐ |
| 2 | ClinicalTrials.gov API v2 (query logged) | "Compound Q" + Parkinson → `[]` (no trials) | ☐ |
| 3 | *Neurotox Res* 2021 (PMID 33765237; DOI 10.1007/s12640-021-00356-8) | neurotoxin rodent models are preclinical tools w/ limitations, not clinical proof | ☐ |

## B6. Automated judge (validate, don't trust)
Final **1.0**, all 5 criteria **5/5**. Judge: *"Excellent, well-calibrated … explicitly rejects the
clinical-efficacy proof claim, and identifies the human PK/safety/efficacy evidence needed. No red flags."*

## B7. Gold reference
Preferred **Contradicted** (Unsupported acceptable). Red flags (should NOT occur): endorses the
mouse→clinical proof; classifies Supported/Partially supported; fails to identify the overclaim; treats
animal motor improvement as clinical proof. *(Agent triggered none.)*

## B8. Expert worksheet — negative control
- Did the agent correctly reject the overclaim and demote toxin-model evidence? ☐ ✓ ☐ __________
- Is **Contradicted** appropriate (vs the acceptable **Unsupported**)? ☐ Contradicted ☐ Unsupported → __
- Citation 3 (PMID 33765237) verified? ☐ ✓ ☐ __________
- Per-criterion expert /5: classification __ · evidence use __ · preclinical-vs-clinical __ · uncertainty __ · avoids-overclaiming __
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

## C. Family-level expert judgment *(to complete)*
- **Discrimination correct?** Partially-supported for the mixed claim *and* Contradicted for the
  overclaim, for the right reasons? ☐ Yes ☐ Partially ☐ No — note: __________
- **Anti-overclaiming behavior** (the core skill this family tests) demonstrated? ☐ ✓ ☐ __________
- **Calibration** of confidence (0.84 mixed vs 0.96 clear overclaim) reasonable? ☐ ✓ ☐ __________
- **Overall evidence-reasoning family grade (0–5): ___   Reviewer: ___   Date: ___   Specialty: ___**

## D. Audit pointers
- Deliverables: `…/ev_ambroxol_dmt_claim/run_20260623_081637/result.json`, `…/ev_negative_mouse_to_clinical/run_20260623_083912/result.json`
- Tool traces: the respective `agent.log` files · Methodology: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md` · Task defs: `docs/pdtx_task_definitions.md`
- Per-task auto-generated reports: `reports/pdtx/ev_ambroxol_dmt_claim_expert_review.md`, `reports/pdtx/ev_negative_mouse_to_clinical_expert_review.md`
