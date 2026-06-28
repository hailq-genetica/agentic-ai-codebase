#!/usr/bin/env python3
"""Generate the PD-TxBench Phase 2.5 seed dataset (small-molecule benchmark).

Phase 2.5 reuses the Phase 2 runner/judge (run_pdtx.py + src/pdtx_eval) but adds
eight small-molecule task families. This script is the single build step for the
seed slice: from the TASKS spec below it writes, for every task,

    tasks/pdtx/phase2_5/<family>/<id>.md      # the agent prompt
    tasks/pdtx/phase2_5/gold/<id>.json        # gold + rubric (schema: rubric_schema_v2 + phase2_5 fields)
    config/pdtx/phase2_5/<family>/<id>.yaml   # runnable config

and a manifest at tasks/pdtx/phase2_5/manifest.jsonl (one line per task, toward the
plan's JSONL dataset splits).

Rubric criteria are pulled from tasks/pdtx/schemas/rubric_phase2_5.json and the
deliverable required-keys from tasks/pdtx/schemas/output_schema_phase2_5.json, so
prompts, gold rubrics, and validation stay in sync. Re-run after editing TASKS.

    python scripts/build_phase2_5_seed.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "tasks" / "pdtx" / "schemas"
TASK_DIR = ROOT / "tasks" / "pdtx" / "phase2_5"
GOLD_DIR = TASK_DIR / "gold"
CONFIG_DIR = ROOT / "config" / "pdtx" / "phase2_5"

AGENT_PROVIDER = "anthropic"
AGENT_MODEL = "claude-opus-4-8"

# task_family -> rubric_id (must exist in rubric_phase2_5.json)
FAMILY_RUBRIC = {
    "target_mechanism_reasoning": "pdtx25_target_mechanism_v1",
    "evidence_verification": "pdtx25_evidence_verification_v1",
    "candidate_smiles_evaluation": "pdtx25_candidate_smiles_v1",
    "admet_cns_assessment": "pdtx25_admet_cns_v1",
    "docking_binding_interpretation": "pdtx25_docking_binding_v1",
    "lead_optimization": "pdtx25_lead_optimization_v1",
    "repurposing_translatability": "pdtx25_repurposing_v1",
    "agentic_smiles_episode": "pdtx25_agentic_episode_v1",
}

# task_family -> the decision field + allowed values stated in the prompt.
DECISION_NOTE = {
    "evidence_verification": "`claim_classification` must be one of "
    "`Supported` / `Partially Supported` / `Unsupported` / `Contradicted` / `Insufficient Evidence`.",
    "candidate_smiles_evaluation": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "admet_cns_assessment": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "docking_binding_interpretation": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "repurposing_translatability": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "agentic_smiles_episode": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
}

TOOLS_PHARM = "external_pharmacology, external_database"
TOOLS_DB = "external_database"

# ---------------------------------------------------------------------------
# Task specification (seed slice). Each task -> one .md + gold + config.
# ---------------------------------------------------------------------------
TASKS = [
    # ---- Family 1: target-mechanism reasoning ----------------------------
    {
        "id": "p25_tmr_gba1_gcase",
        "family": "target_mechanism_reasoning",
        "difficulty": "easy",
        "neg": False,
        "title": "GCase enhancement in GBA1-associated Parkinson's disease",
        "intro": "Explain the therapeutic rationale for a GCase-enhancing small molecule and identify the main uncertainties.",
        "context": [
            "**Disease context:** GBA1-associated Parkinson's disease (carriers of *GBA1* variants).",
            "**Proposed target / MoA:** enhance glucocerebrosidase (GCase) activity (e.g. pharmacological chaperone or activator).",
        ],
        "job": [
            "Describe the GBA1 -> GCase -> lysosome -> alpha-synuclein axis and how the target relates to PD.",
            "State why GCase is a therapeutically relevant target and which patient subgroup it addresses.",
            "Identify the main mechanistic and evidentiary uncertainties.",
            "Be explicit that mechanistic plausibility is not proven clinical disease modification.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Mechanistically plausible target; not proven disease-modifying",
        "gold_rationale": "GBA1 encodes GCase; reduced GCase activity impairs lysosomal function and is linked to alpha-synuclein accumulation, defining a GBA1-associated PD subgroup. GCase enhancement is therefore mechanistically plausible, but clinical disease modification has not been established and must not be claimed.",
        "required_concepts": [
            "GBA1", "glucocerebrosidase", "lysosomal", "alpha-synuclein",
            "GBA1-associated subgroup", "pharmacological chaperone", "disease modification not proven",
        ],
        "acceptable_variants": [
            "GCase", "lysosome", "a-synuclein", "α-synuclein", "synuclein",
            "GBA1 carriers", "patient subgroup", "not proven", "unproven clinically",
        ],
        "red_flags": [
            "claims proven disease modification without sufficient clinical evidence",
            "confuses symptomatic effect with disease modification",
        ],
    },
    {
        "id": "p25_tmr_neg_maob_symptomatic",
        "family": "target_mechanism_reasoning",
        "difficulty": "medium",
        "neg": True,
        "title": "MAO-B inhibition: symptomatic vs disease-modifying",
        "intro": "Explain the role of MAO-B inhibition in Parkinson's disease and whether it modifies the disease course.",
        "context": [
            "**Disease context:** idiopathic Parkinson's disease, symptomatic management.",
            "**Proposed target / MoA:** small-molecule MAO-B inhibition to raise synaptic dopamine.",
        ],
        "job": [
            "Explain how MAO-B inhibition affects dopamine metabolism and symptoms.",
            "State whether the mechanism is symptomatic or disease-modifying, with justification.",
            "Identify the main uncertainties and what evidence would be needed for a disease-modification claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Symptomatic dopaminergic mechanism; not disease-modifying",
        "gold_rationale": "MAO-B inhibition reduces dopamine breakdown and gives symptomatic benefit. Trials designed to show neuroprotection/disease modification have not established it; a strong answer keeps this symptomatic and does not claim disease modification.",
        "required_concepts": [
            "MAO-B", "dopamine metabolism", "symptomatic", "not disease-modifying",
            "neuroprotection not established",
        ],
        "acceptable_variants": [
            "monoamine oxidase B", "symptomatic benefit", "dopamine breakdown",
            "disease modification not proven", "no disease modification",
        ],
        "red_flags": [
            "claims MAO-B inhibition is disease-modifying or neuroprotective",
            "confuses symptomatic effect with disease modification",
        ],
    },
    # ---- Family 2: evidence verification ---------------------------------
    {
        "id": "p25_ev_ambroxol_dmt_claim",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": False,
        "title": "Claim check: ambroxol as a disease-modifying PD therapy",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Ambroxol is a proven disease-modifying therapy for Parkinson's disease.\"",
            "**Background:** ambroxol is a GCase chaperone with mechanistic plausibility and early/biomarker clinical signals; definitive randomized disease-modification outcomes are not established (e.g. confirmatory phase 3 ongoing).",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Summarize supporting and limiting evidence and state the highest evidence level reached.",
            "State the main uncertainty and why the word 'proven' is or is not justified.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Partially Supported",
        "acceptable_decisions": ["Insufficient Evidence"],
        "gold_label": "Partially Supported — mechanistic + early clinical signals, not proven disease modification",
        "gold_rationale": "There is mechanistic plausibility and early/biomarker clinical investigation, but no definitive randomized outcome establishing disease modification. The claim of a 'proven' disease-modifying therapy is therefore only partially supported; calling it proven is an overclaim.",
        "required_concepts": [
            "GCase chaperone", "early clinical evidence", "not proven", "disease modification",
            "main uncertainty",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "biomarker evidence", "phase 3 ongoing", "no definitive RCT",
            "randomized outcome", "overclaim",
        ],
        "red_flags": [
            "treats early or biomarker clinical evidence as proven disease modification",
            "classifies the 'proven' claim as fully Supported",
        ],
    },
    {
        "id": "p25_ev_neg_caffeine_causation",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": True,
        "title": "Claim check: caffeine as a disease-modifying treatment (association vs causation)",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Because higher caffeine intake is associated with lower Parkinson's disease risk, caffeine is a disease-modifying treatment for PD.\"",
            "**Background:** the evidence is observational/epidemiological association; an interventional trial of caffeine did not show symptomatic or disease-modifying benefit.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Explain the association-versus-causation distinction and the evidence level.",
            "State what evidence would be required to support a disease-modifying treatment claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Unsupported",
        "acceptable_decisions": ["Contradicted", "Insufficient Evidence"],
        "gold_label": "Unsupported — epidemiological association does not establish a disease-modifying treatment",
        "gold_rationale": "A protective epidemiological association is not evidence of a treatment effect; causation cannot be inferred from observational association, and interventional data do not support benefit. The treatment claim is unsupported.",
        "required_concepts": [
            "association is not causation", "observational", "epidemiological",
            "interventional trial", "disease modification not supported",
        ],
        "acceptable_variants": [
            "correlation", "confounding", "no causal", "randomized trial", "no benefit",
            "reverse causation",
        ],
        "red_flags": [
            "infers causation from an observational association",
            "treats epidemiological association as clinical treatment efficacy",
        ],
    },
    # ---- Family 3: candidate SMILES evaluation ---------------------------
    {
        "id": "p25_smiles_gba1_chaperone",
        "family": "candidate_smiles_evaluation",
        "difficulty": "medium",
        "neg": False,
        "title": "Evaluate a GCase chaperone candidate for GBA1-associated PD",
        "intro": "Evaluate whether this small-molecule candidate should progress to experimental validation.",
        "context": [
            "**Disease context:** GBA1-associated Parkinson's disease.",
            "**Proposed target / MoA:** GCase pharmacological chaperone.",
        ],
        "data_block": {
            "candidate_name": "Ambroxol analog A",
            "smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O",
            "known_or_hypothetical": "analog",
        },
        "job": [
            "Assess PD relevance (GBA1 -> GCase -> lysosome -> alpha-synuclein) and MoA plausibility.",
            "Assess CNS drug-likeness and BBB penetration likelihood (this is a CNS target).",
            "Assess ADMET and safety liabilities (solubility, clearance, CYP, hERG, AMES, DILI).",
            "Give a calibrated go_no_go decision and the single most informative next experiment.",
            "Distinguish mechanistic plausibility from proven disease modification.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go — plausible chaperone, conditional on CNS exposure + ADMET clearance",
        "gold_rationale": "A GCase chaperone is mechanistically well-aligned with GBA1-associated PD. Progression should be conditional on confirming CNS/BBB exposure and clearing standard ADMET/safety liabilities; mechanistic plausibility is not proven disease modification.",
        "required_concepts": [
            "GCase", "GBA1", "lysosomal", "alpha-synuclein", "pharmacological chaperone",
            "blood-brain barrier", "ADMET", "safety liability", "next experiment",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "BBB", "blood brain barrier", "a-synuclein", "α-synuclein",
            "synuclein", "chaperone", "CNS penetration", "GCase activity assay", "target engagement",
        ],
        "red_flags": [
            "claims proven disease modification without sufficient clinical evidence",
            "ignores blood-brain barrier / CNS penetration",
            "ignores ADMET or safety liabilities",
            "treats docking/binding as proof of efficacy",
        ],
    },
    {
        "id": "p25_smiles_neg_herg_bbb",
        "family": "candidate_smiles_evaluation",
        "difficulty": "hard",
        "neg": True,
        "title": "Candidate with strong docking but poor BBB and hERG liability",
        "intro": "Evaluate whether this small-molecule candidate should progress to experimental validation.",
        "context": [
            "**Disease context:** Parkinson's disease, CNS target.",
            "**Proposed target / MoA:** CNS enzyme modulation (binding hypothesis from docking).",
        ],
        "data_block": {
            "candidate_name": "Compound H",
            "smiles": "O=C(Nc1ccc(cc1)C(F)(F)F)c1ccc2c(c1)cccc2-c1ccccc1",
            "docking": {"score_kcal_mol": -10.2, "reference_ligand_kcal_mol": -7.8},
            "admet": {"bbb": "low", "herg": "high risk", "solubility": "poor"},
        },
        "job": [
            "Assess whether the docking score justifies progression on its own.",
            "Weigh the poor predicted BBB penetration for a CNS target and the hERG liability.",
            "Give a calibrated go_no_go decision and the next experiment if any.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — strong docking cannot rescue poor CNS exposure + hERG liability",
        "gold_rationale": "A favourable docking score does not prove activity or CNS exposure. With low predicted BBB penetration for a CNS target and a hERG cardiotoxicity liability, the candidate should not progress as-is; docking must not override exposure and safety.",
        "required_concepts": [
            "docking is not proof of efficacy", "blood-brain barrier", "CNS exposure",
            "hERG", "No-Go",
        ],
        "acceptable_variants": [
            "BBB", "brain penetration", "cardiotoxicity", "hERG liability", "poor exposure",
            "binding is not engagement",
        ],
        "red_flags": [
            "recommends Go based on the docking score despite poor BBB",
            "ignores the hERG liability",
            "treats docking score as proof of efficacy",
        ],
    },
    # ---- Family 4: ADMET / CNS assessment --------------------------------
    {
        "id": "p25_admet_neg_herg_cyp",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": True,
        "title": "ADMET review of a chronic-use PD candidate with multiple liabilities",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress for chronic PD use.",
        "context": [
            "**Therapeutic context:** chronic, long-term disease-modifying therapy for Parkinson's disease (CNS target).",
        ],
        "data_block": {
            "candidate": "Compound X",
            "predicted_properties": {
                "bbb": "low",
                "caco2": "high",
                "ames": "negative",
                "herg": "high risk",
                "cyp3a4_inhibitor": "yes",
                "solubility": "poor",
            },
        },
        "job": [
            "Interpret BBB/CNS exposure for a brain target.",
            "Interpret the toxicology and PK liabilities (hERG, CYP3A4, solubility) for chronic dosing.",
            "Give a calibrated go_no_go that follows from the ADMET profile, not from target relevance alone.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go (or Conditional Go only after substantial optimization)",
        "gold_rationale": "Low BBB undermines a CNS target; hERG high risk, CYP3A4 inhibition (DDI risk), and poor solubility are serious liabilities for a chronic therapy. Target relevance does not justify a Go; the profile warrants No-Go or optimization first.",
        "required_concepts": [
            "low BBB", "CNS exposure", "hERG", "CYP3A4 drug-drug interaction", "poor solubility",
            "chronic-use safety", "No-Go",
        ],
        "acceptable_variants": [
            "blood-brain barrier", "brain penetration", "cardiotoxicity", "DDI", "CYP inhibition",
            "long-term safety", "optimization required",
        ],
        "red_flags": [
            "recommends Go on target relevance while ignoring the ADMET liabilities",
            "ignores the low BBB for a CNS target",
            "ignores the hERG liability",
            "ignores the CYP3A4 drug-drug interaction risk",
        ],
    },
    {
        "id": "p25_admet_lrrk2_balanced",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": False,
        "title": "ADMET review of a brain-penetrant LRRK2 inhibitor",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress.",
        "context": [
            "**Therapeutic context:** LRRK2 kinase inhibition for LRRK2-associated Parkinson's disease (CNS target, chronic dosing).",
        ],
        "data_block": {
            "candidate": "LRRK2-inh B",
            "predicted_properties": {
                "bbb": "moderate-high",
                "ames": "negative",
                "herg": "low risk",
                "cyp3a4_inhibitor": "no",
                "solubility": "moderate",
            },
            "class_note": "LRRK2 inhibitors as a class carry peripheral on-target concerns (e.g. lung type II pneumocyte / kidney changes).",
        },
        "job": [
            "Interpret the CNS exposure and core ADMET profile.",
            "Address the LRRK2 class peripheral on-target safety concern and a therapeutic-window strategy.",
            "Give a calibrated go_no_go with the next safety experiment.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go — clean core ADMET, conditional on managing LRRK2 peripheral safety window",
        "gold_rationale": "Core ADMET is acceptable (moderate-high BBB, AMES negative, low hERG, no CYP3A4 issue). The principal risk is the LRRK2 class peripheral on-target effect; progression is conditional on a therapeutic-window / peripheral-safety strategy.",
        "required_concepts": [
            "LRRK2", "CNS exposure", "peripheral on-target safety", "therapeutic window",
            "Conditional Go",
        ],
        "acceptable_variants": [
            "blood-brain barrier", "brain penetration", "lung safety", "type II pneumocyte",
            "kidney", "safety margin", "selectivity",
        ],
        "red_flags": [
            "ignores the LRRK2 peripheral / lung on-target safety concern",
            "overclaims disease modification from a clean ADMET profile",
        ],
    },
    # ---- Family 5: docking / binding interpretation ----------------------
    {
        "id": "p25_docking_gcase_interpretation",
        "family": "docking_binding_interpretation",
        "difficulty": "medium",
        "neg": False,
        "title": "Interpret a GCase docking result without overclaiming",
        "intro": "Interpret the docking/binding evidence for this compound and recommend a decision.",
        "context": [
            "**Target:** GCase (GBA1 product), ambroxol-like pocket.",
        ],
        "data_block": {
            "compound": "Compound Y",
            "docking_score_kcal_mol": -8.7,
            "reference_ligand_score_kcal_mol": -7.9,
            "binding_site": "ambroxol-like pocket",
            "admet_summary": "poor predicted BBB and hERG risk",
        },
        "job": [
            "State what the docking score does and does not establish relative to the reference ligand.",
            "Integrate the ADMET concerns (BBB, hERG) into the interpretation.",
            "Recommend a go_no_go and a biochemical/cellular target-engagement validation experiment.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["No-Go"],
        "gold_label": "Conditional Go — binding hypothesis only; requires target-engagement validation and ADMET fixes",
        "gold_rationale": "A docking score modestly better than the reference supports a binding hypothesis but does not prove activity, target engagement, CNS exposure, or efficacy. With poor BBB and hERG risk, progression is conditional on biochemical/cellular validation and ADMET mitigation.",
        "required_concepts": [
            "docking is not proof of efficacy", "reference ligand", "target engagement",
            "blood-brain barrier", "hERG", "validation experiment",
        ],
        "acceptable_variants": [
            "binding hypothesis", "pose quality", "BBB", "brain penetration", "cardiotoxicity",
            "GCase activity assay", "cellular assay", "biochemical assay",
        ],
        "red_flags": [
            "treats the docking score as proof of efficacy",
            "ignores the reference ligand context",
            "ignores ADMET in the interpretation",
            "claims disease modification from docking alone",
        ],
    },
    # ---- Family 6: lead optimization -------------------------------------
    {
        "id": "p25_leadopt_gcase_chaperone",
        "family": "lead_optimization",
        "difficulty": "medium",
        "neg": False,
        "title": "Optimize a GCase chaperone analog with solubility and hERG liabilities",
        "intro": "Propose a rational lead-optimization strategy for this scaffold.",
        "context": [
            "**Scaffold:** GCase pharmacological chaperone analog (CNS target).",
            "**Profile:** good predicted target binding, but poor solubility and high hERG risk.",
        ],
        "job": [
            "State the optimization goal and the liabilities to address.",
            "Propose chemistry-aware modifications, each with an explicit rationale, expected benefit, and risk.",
            "Preserve the pharmacophore and CNS penetration while fixing the liabilities.",
            "List the properties to re-check and the experimental validation step.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Rational, pharmacophore-preserving optimization addressing solubility and hERG",
        "gold_rationale": "A strong answer targets the named liabilities with justified medicinal-chemistry changes (e.g. add polarity/ionizable group to improve solubility, remove basic/lipophilic hERG-associated features) while preserving the chaperone pharmacophore and CNS penetration, then re-checks properties and validates experimentally. Arbitrary changes without rationale are penalized.",
        "required_concepts": [
            "solubility", "hERG", "preserve pharmacophore", "CNS penetration",
            "rationale for each modification", "recheck properties", "experimental validation",
        ],
        "acceptable_variants": [
            "lipophilicity", "logP", "polarity", "ionizable group", "reduce basicity",
            "blood-brain barrier", "brain penetration", "target engagement", "re-test",
        ],
        "red_flags": [
            "proposes arbitrary chemical modifications without rationale",
            "destroys CNS penetration / pharmacophore while fixing a liability",
        ],
    },
    # ---- Family 7: repurposing / translatability -------------------------
    {
        "id": "p25_repurpose_lysosomal",
        "family": "repurposing_translatability",
        "difficulty": "medium",
        "neg": False,
        "title": "Repurposing a marketed lysosomal-modulating drug for PD",
        "intro": "Evaluate whether this marketed drug is a strong repurposing candidate for Parkinson's disease.",
        "context": [
            "**Candidate:** a marketed small molecule with an established human safety/dosing record that modulates lysosomal/autophagy function.",
            "**Hypothesis:** lysosomal enhancement could be relevant to GBA1-associated / lysosomal-dysfunction PD.",
        ],
        "job": [
            "Give the repurposing rationale and mechanism match to PD.",
            "Use the existing human safety and dosing data; reason about CNS exposure at tolerated human doses.",
            "Interpret available clinical evidence and distinguish symptomatic from disease-modifying use.",
            "Propose endpoints/biomarkers and patient-subgroup selection; give a calibrated go_no_go.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go", "No-Go"],
        "gold_label": "Conditional Go — leverage human safety, conditional on CNS exposure + subgroup/biomarker strategy",
        "gold_rationale": "Repurposing benefits from existing human safety/dosing, but the case hinges on confirming CNS exposure at tolerated doses, a mechanism-matched patient subgroup (e.g. GBA1/lysosomal), and a biomarker/endpoint strategy. Disease modification must not be assumed; default is Conditional Go pending CNS-exposure and subgroup data.",
        "required_concepts": [
            "human safety data", "dosing", "CNS exposure", "mechanism match", "biomarker",
            "patient subgroup", "symptomatic vs disease-modifying",
        ],
        "acceptable_variants": [
            "tolerated dose", "blood-brain barrier", "brain penetration", "GBA1 subgroup",
            "endpoint", "drug-drug interaction", "trial design",
        ],
        "red_flags": [
            "assumes CNS exposure without data",
            "overclaims disease modification from a marketed-drug mechanism",
        ],
    },
    # ---- Family 8: agentic small-molecule episode ------------------------
    {
        "id": "p25_agentic_gba1_smiles",
        "family": "agentic_smiles_episode",
        "difficulty": "hard",
        "neg": False,
        "title": "Agentic evaluation of a new small molecule for GBA1-associated PD",
        "intro": "Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.",
        "context": [
            "**Goal:** evaluate a new small molecule as a candidate for GBA1-associated Parkinson's disease.",
            "**Proposed target / MoA:** GCase modulation.",
        ],
        "data_block": {
            "candidate_name": "Compound Z",
            "smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Cl)Cl)N)O",
            "proposed_target": "GCase",
        },
        "job": [
            "Form a PD mechanism hypothesis for the candidate.",
            "Use tools (literature, knowledge graph, docking, ADMET, patent/novelty, clinical) and build an evidence_table integrating the findings.",
            "Assess ADMET/safety and IP/novelty risk.",
            "Give a calibrated go_no_go with decision_rationale and the next experiment.",
            "Keep the workflow auditable: record which tools were used and why.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["No-Go", "Go"],
        "gold_label": "Conditional Go — evidence-grounded, conditional on CNS exposure + ADMET/IP clearance",
        "gold_rationale": "A strong episode forms a correct GCase/GBA1 mechanism hypothesis, integrates tool/literature evidence into a table, assesses ADMET/safety and novelty/IP, and reaches a calibrated decision with a decision-relevant next experiment (e.g. GCase target-engagement assay). The default is Conditional Go pending CNS exposure and ADMET/IP clearance; no overclaiming of disease modification.",
        "required_concepts": [
            "GCase", "GBA1", "evidence table", "ADMET", "blood-brain barrier",
            "novelty or patent risk", "go_no_go", "next experiment",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "BBB", "brain penetration", "IP risk", "patent",
            "target engagement", "GCase activity assay", "tool trace",
        ],
        "red_flags": [
            "skips ADMET / CNS exposure assessment",
            "claims proven disease modification without sufficient clinical evidence",
            "reaches a decision without proposing a validation experiment",
        ],
    },
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def _load(path):
    with open(path) as f:
        return json.load(f)


def render_prompt(task, required_keys, decision_note):
    family = task["family"]
    lines = [
        "You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting "
        "as a therapeutic-discovery assistant.",
        "",
        f"## Task: {task['title']}",
        task["intro"],
        "",
        "### Context",
    ]
    lines += [f"- {c}" for c in task["context"]]

    if task.get("data_block"):
        lines += ["", "### Provided data", "```json", json.dumps(task["data_block"], indent=2), "```"]

    lines += ["", "### Your job"]
    lines += [f"{i}. {step}" for i, step in enumerate(task["job"], 1)]

    lines += [
        "",
        "### Available tools",
        "You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, "
        "docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, "
        "ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and "
        "`run_python_repl`. Ground your assessment in evidence rather than memory where possible, and "
        "cite what you used.",
        "",
        "### Deliverable (write to the run's output directory)",
        "> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run "
        "directory. Do **not** reassign it or invent a path. Write exactly to `f\"{output_dir}/result.json\"` "
        "and `f\"{output_dir}/reasoning.txt\"`.",
        f"- **`result.json`** — a JSON object matching the `{family}` definition in "
        f"`tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: "
        f"{', '.join('`' + k + '`' for k in required_keys)}.",
    ]
    if decision_note:
        lines[-1] = lines[-1] + f" {decision_note}"
    lines += [
        "  Generate the file programmatically (e.g. `json.dump(..., open(f\"{output_dir}/result.json\",\"w\"))`); "
        "do not hand-write it.",
        "- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you "
        "handled uncertainty.",
        "",
    ]
    return "\n".join(lines)


def render_gold(task, rubric_catalog):
    family = task["family"]
    rubric_id = FAMILY_RUBRIC[family]
    criteria = rubric_catalog["rubrics"][rubric_id]["criteria"]
    return {
        "task_id": task["id"],
        "phase": "phase2_5",
        "category": "small_molecule",
        "task_family": family,
        "is_negative_control": task["neg"],
        "rubric_id": rubric_id,
        "gold_label": task["gold_label"],
        "preferred_decision": task["preferred_decision"],
        "acceptable_decisions": task["acceptable_decisions"],
        "gold_rationale": task["gold_rationale"],
        "required_concepts": task["required_concepts"],
        "acceptable_variants": task["acceptable_variants"],
        "red_flags": task["red_flags"],
        "rubric": {"criteria": criteria},
    }


def render_config(task):
    family = task["family"]
    tid = task["id"]
    return (
        f"task_file: tasks/pdtx/phase2_5/{family}/{tid}.md\n"
        f"gold_file: tasks/pdtx/phase2_5/gold/{tid}.json\n"
        f"category: small_molecule\n"
        f"task_family: {family}\n"
        f"tool_category: {task['tools']}\n"
        f"reasoning_effort: high\n"
        f"interactive: false        # overridden by run_pdtx.py --mode\n"
        f"capture_telemetry: true\n"
        f"output_base_dir: output/pdtx/phase2_5/{family}/{tid}/\n"
        f"\n"
        f"llm:\n"
        f"  provider: {AGENT_PROVIDER}\n"
        f"  model: {AGENT_MODEL}\n"
        f"logging:\n"
        f"  enabled: false          # set true (+ project/entity) to log to W&B/Weave\n"
    )


def main():
    rubric_catalog = _load(SCHEMA_DIR / "rubric_phase2_5.json")
    output_schema = _load(SCHEMA_DIR / "output_schema_phase2_5.json")

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    manifest_lines = []
    seen = set()

    for task in TASKS:
        tid, family = task["id"], task["family"]
        if tid in seen:
            raise ValueError(f"duplicate task_id: {tid}")
        seen.add(tid)
        if family not in FAMILY_RUBRIC:
            raise ValueError(f"{tid}: unknown family {family}")
        required_keys = output_schema["definitions"][family]["required"]

        (TASK_DIR / family).mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / family).mkdir(parents=True, exist_ok=True)

        (TASK_DIR / family / f"{tid}.md").write_text(
            render_prompt(task, required_keys, DECISION_NOTE.get(family, ""))
        )
        (GOLD_DIR / f"{tid}.json").write_text(
            json.dumps(render_gold(task, rubric_catalog), indent=2) + "\n"
        )
        (CONFIG_DIR / family / f"{tid}.yaml").write_text(render_config(task))

        manifest_lines.append(json.dumps({
            "task_id": tid,
            "phase": "phase2_5",
            "category": "small_molecule",
            "task_family": family,
            "difficulty": task["difficulty"],
            "is_negative_control": task["neg"],
            "preferred_decision": task["preferred_decision"],
            "task_file": f"tasks/pdtx/phase2_5/{family}/{tid}.md",
            "gold_file": f"tasks/pdtx/phase2_5/gold/{tid}.json",
            "config_file": f"config/pdtx/phase2_5/{family}/{tid}.yaml",
        }))

    (TASK_DIR / "manifest.jsonl").write_text("\n".join(manifest_lines) + "\n")

    n_neg = sum(1 for t in TASKS if t["neg"])
    families = sorted({t["family"] for t in TASKS})
    print(f"Wrote {len(TASKS)} Phase 2.5 seed tasks ({n_neg} negative controls) "
          f"across {len(families)} families:")
    for fam in families:
        ids = [t["id"] for t in TASKS if t["family"] == fam]
        print(f"  - {fam}: {len(ids)} ({', '.join(ids)})")
    print(f"Manifest: {TASK_DIR / 'manifest.jsonl'}")


if __name__ == "__main__":
    main()
