# PD-TxBench Expert Review Report — Small-Molecule Family

**Tasks:** `sm_gba1_ambroxol_analog` (positive) + `sm_negative_herg_bbb` (negative control)
**Family:** small_molecule  ·  **Agent + judge:** `gpt-5.5-2026-04-23` (provider: openai)

> Packaged for **independent expert review**. The two tasks are a matched pair: the suite tests not just
> whether the agent scores each one, but whether it **discriminates** — advancing a credible GBA1-PD
> candidate while killing a structurally-doomed one. The automated LLM-judge scores (§4) are a starting
> point, **not** the verdict; complete the worksheets in §6. Treat every factual claim and citation as
> **the agent's assertion, to be verified** (single-model self-grading caveat applies — agent and judge
> are the same model).

---

## 0. Discrimination summary (read this first)

| | `sm_gba1_ambroxol_analog` (positive) | `sm_negative_herg_bbb` (negative control) |
|---|---|---|
| Scenario | GCase chaperone candidate for GBA1-PD | "Compound X": strong GCase docking, **poor BBB + hERG** |
| **Agent decision** | **Conditional Go** (conf 0.72) | **No-Go** (conf 0.88) |
| Gold decision | Conditional Go (Go acceptable) | No-Go (Conditional Go acceptable) |
| Decision match | ✅ match | ✅ match |
| Automated score | 1.0 (7/7 = 5) | 1.0 (7/7 = 5) |
| Red flags | none | none |
| Effort (tool calls / tokens) | heavy: 128 calls, ~3.44M tok | lean: 11 calls, ~107k tok |

**The discrimination is correct and well-reasoned.** The agent advanced the mechanistically credible
GBA1 candidate *conditionally* (not an unqualified Go — it flagged unproven disease modification and an
IP problem), and **killed** the negative control on developability (CNS exposure) + cardiac (hERG)
grounds, explicitly refusing to let a strong docking score drive progression. Notably it spent ~30×
more effort on the genuine candidate than on the obvious kill — appropriate triage.

The reviewer's job: confirm the **quantitative claims and citations** below, and decide whether the two
decisions are correct on the merits.

---

# PART A — `sm_gba1_ambroxol_analog` (positive)

## A1. Provenance
Run `run_20260623_090653` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**127 steps / 128 tool calls (4 handled failures)** · ~3.44M tokens · judge `gpt-5.5-2026-04-23`.
Artifacts: `output/pdtx/small_molecule/sm_gba1_ambroxol_analog/run_20260623_090653/`.

## A2. Question
Evaluate "Ambroxol analog A" (SMILES given) as a GCase pharmacological chaperone for GBA1-associated PD;
reason through disease relevance, MoA, docking, BBB, ADMET/safety, patent/novelty → Go/No-Go + next experiment.

## A3. Agent decision
> **Conditional Go** · confidence **0.72**.

## A4. Key findings the agent reported *(verify each)*
- **Candidate identity:** SMILES → **PubChem CID 2132 = ambroxol** (not a novel analog). The agent
  surfaced this itself, making it the dominant **novelty/FTO problem**.
- **Target relevance:** GBA1→GCase→lysosome→α-synuclein axis; cited **NEJM 2009** GBA1-PD genetic
  association and the **JAMA Neurol 2020** ambroxol PD trial.
- **Docking:** AutoDock Vina via TDC/pyscreener on **PDB 3KE0** (N370S GCase, acidic pH; box on catalytic
  Glu235/Glu340), **−7.0 kcal/mol** — interpreted as "plausible but modest," explicitly *not* proof of
  pH-dependent chaperoning. (Correct, calibrated use of docking.)
- **ADMET (per axis, with model values):**
  - BBB: favorable — DeepPurpose 0.94 (MPNN) / 0.997 (Morgan); consistent with ambroxol clinical CSF data
  - AMES: 0.42 (equivocal; aryl-amine/brominated motif → needs experimental confirmation)
  - hERG: 0.33 (moderate-low; confirm by patch-clamp)
  - DILI: 0.47 (equivocal/monitor); CYP: **2D6 0.85–1.0, 1A2 0.73–0.97 (flagged)**, 3A4 low
  - Solubility: borderline (PubChem >56.7 µg/mL pH 7.4; physchem MW 378.1, cLogP 3.19, TPSA 58.3)
  - Clearance/half-life: moderate-high
- **Patent/novelty:** high FTO risk for composition-of-matter (the structure *is* ambroxol); crowded
  repurposing IP.
- **Next experiment:** concentration-response **target-engagement/rescue in GBA1-variant patient
  iPSC-DA neurons** (GCase maturation/trafficking + activity + α-synuclein burden) at matched unbound
  concentrations; progress only if net lysosomal GCase activity rises without inhibition/cytotoxicity.

## A5. Citations to verify
| # | Source | Claim | ✓ |
|---|---|---|:--:|
| 1 | NEJM 2009 (Sidransky et al., multicenter) | GBA1 mutations associated with PD risk | ☐ |
| 2 | JAMA Neurology 2020 (ambroxol PD trial) | safety/CSF penetration/target engagement; biomarker ≠ proven efficacy | ☐ |
| 3 | ClinicalTrials.gov NCT02941822 | completed phase 2, n=23, "Ambroxol in Disease Modification in PD" | ☐ |
| 4 | RCSB PDB 3KE0 | N370S GCase structure used for docking box | ☐ |
| 5 | PubChem CID 2132 | SMILES = ambroxol; physchem; patent records | ☐ |
| (model outputs) | DeepPurpose / TDC RF / Vina | BBB/AMES/hERG/DILI/CYP/clearance + docking values above | ☐ |

## A6. Automated judge (validate, don't trust)
Final **1.0**; all 7 criteria **5/5** (mechanism, target/MoA, ADMET, safety, Go/No-Go, next experiment,
uncertainty). Judge: *"Excellent, expert-level … appropriately cautious about translating mechanistic
chaperoning, docking, or biomarker evidence into disease-modifying efficacy … no red-flag overclaims."*

## A7. Gold reference
Preferred **Conditional Go** (Go acceptable). Required concepts: GCase, GBA1, lysosomal, α-synuclein,
pharmacological chaperone, BBB, ADMET, safety liability, next experiment. Red flags: claims proven
disease modification; ignores BBB; ignores ADMET/safety; treats docking as proof. *(Agent triggered none.)*

## A8. Expert worksheet — positive
- Citations 1–5 verified? ☐ all ✓ ☐ issues: __________ · ADMET model values plausible? ☐ ☐ __________
- Docking interpretation sound (−7.0 = "modest, not proof")? ☐ ✓ ☐ __________
- Per-criterion expert /5: mechanism __ · target/MoA __ · ADMET __ · safety __ · decision __ · next-exp __ · uncertainty __
- Agree with **Conditional Go**? ☐ Agree ☐ Disagree → __________ · Most important gap: __________
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

# PART B — `sm_negative_herg_bbb` (negative control)

## B1. Provenance
Run `run_20260623_084935` · model `gpt-5.5-2026-04-23` (openai, effort high) · autonomous ·
**10 steps / 11 tool calls (0 failures)** · ~107k tokens · judge `gpt-5.5-2026-04-23`.
Artifacts: `output/pdtx/small_molecule/sm_negative_herg_bbb/run_20260623_084935/`.

## B2. Question
"Compound X" has strong predicted GCase docking **but** poor BBB penetration and a strong hERG liability.
Decide whether it should progress.

## B3. Agent decision
> **No-Go** · confidence **0.88**.

## B4. Key findings the agent reported *(verify each)*
- **Docking correctly demoted:** favorable GCase docking = a target-engagement *hypothesis* only; "not
  sufficient evidence for a CNS therapeutic."
- **BBB — not acceptable:** provided ADMET predicts poor BBB + P-gp efflux; independent physchem check
  on the SMILES gives **TPSA 132.8 Å², MW 467.5, cLogP 1.94, HBA 7, HBD 2**, all unfavorable for passive
  CNS exposure → low probability of sufficient unbound brain concentration.
- **hERG — development-stopping:** strong predicted hERG inhibition is a serious QT/cardiac liability for
  a chronic PD drug and is **not rescued by docking affinity**.
- **Decision logic:** explicitly refuses to let a good docking score override the BBB + hERG liabilities.
- **Next step:** *not* efficacy progression — a **kill/diagnostic package** (manual patch-clamp hERG +
  bidirectional MDCK-MDR1/PAMPA-BBB permeability), redesign only if the chemotype is retained, with a
  decision gate (acceptable hERG margin + high passive permeability/low efflux) before re-testing GCase.

## B5. Citations to verify
The deliverable carries **no structured `evidence_used`** (it reasoned from the provided ADMET signals +
its own physicochemical computation rather than literature). Verify the **computed physchem values**
(TPSA 132.8 Å², MW 467.5, cLogP 1.94) from the SMILES, and that the BBB/hERG conclusions follow. Tool
trace: `calculate_physicochemical_properties` ×1, `predict_admet_properties` ×1, `run_python_repl` ×8.

## B6. Automated judge (validate, don't trust)
Final **1.0**; all 7 criteria **5/5**. Judge: *"Excellent, well-calibrated negative-control response …
correctly demotes docking to insufficient evidence, prominently identifies BBB/CNS penetration and hERG
cardiac safety liabilities, and makes the preferred No-Go decision with appropriate kill/redesign next steps."*

## B7. Gold reference
Preferred **No-Go** (Conditional Go acceptable). Red flags (should NOT occur): issues a Go driven by
docking despite the liabilities; ignores BBB; ignores hERG; treats strong binding as sufficient.
*(Agent triggered none.)*

## B8. Expert worksheet — negative control
- Physchem values correct from SMILES (TPSA/MW/cLogP)? ☐ ✓ ☐ __________
- Did the agent correctly subordinate docking to the BBB/hERG liabilities? ☐ ✓ ☐ __________
- Per-criterion expert /5: mechanism __ · target/MoA __ · ADMET __ · safety __ · decision __ · next-exp __ · uncertainty __
- Agree with **No-Go**? ☐ Agree ☐ Disagree → __________
- Overall grade (0–5): ___  Reviewer: ___  Date: ___

---

## C. Family-level expert judgment *(to complete)*
- **Discrimination correct?** Did the agent advance the real candidate *and* kill the trap for the right
  reasons? ☐ Yes ☐ Partially ☐ No — note: __________
- **Calibration:** Is Conditional-Go-vs-No-Go the right split here (not both Go, not both No-Go)? ☐ ✓ ☐ __
- **Effort allocation** (heavy on candidate, light on kill) appropriate? ☐ ✓ ☐ __
- **Overall small-molecule family grade (0–5): ___   Reviewer: ___   Date: ___   Specialty: ___**

## D. Audit pointers
- Deliverables: `…/sm_gba1_ambroxol_analog/run_20260623_090653/result.json`, `…/sm_negative_herg_bbb/run_20260623_084935/result.json`
- Tool traces: the respective `agent.log` files · Methodology: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md` · Task defs: `docs/pdtx_task_definitions.md`
- Per-task auto-generated reports also exist: `reports/pdtx/sm_gba1_ambroxol_analog_expert_review.md`, `reports/pdtx/sm_negative_herg_bbb_expert_review.md`
