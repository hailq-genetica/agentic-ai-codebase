# Benchmark Tasks v2

## Guiding Philosophy

These tasks benchmark whether **unbiased transcriptional programs** discovered by cNMF on tumor-compartment scRNA-seq (from a scMultiome discovery dataset) recapitulate known, well-established axes of cancer biology when transferred to an independent TCGA validation cohort.

The design principles are:

1. **Benchmark the common, not the exotic.** Because cNMF discovery is unbiased, we validate against axes that are expected to emerge in any competent decomposition — major molecular subtypes, histological grades, and survival-associated programs with large effect sizes. If a well-known axis doesn't appear, that's informative. If a novel axis appears, that's discovery — but it can't be benchmarked here.

2. **Two-tier validation: transfer first, then ground.** Tier 1 asks whether program activity scores computed from bulk RNA-seq correlate with the target variable — testing whether single-cell-derived gene lists produce meaningful signal in bulk. Tier 2 asks whether programs enrich in condition-stratified DE gene lists, where the condition label comes from a non-transcriptomic source (DNA mutations, protein IHC, pathologist grading, clinical endpoints) — testing whether the transcriptional signal is anchored in biology beyond RNA.

3. **Validation labels must be trustworthy and available.** We only create tasks where TCGA provides high-quality labels: mutation calls from WES, IHC/FISH from standardized pathology, WHO-graded histological features, and curated clinical endpoints (TCGA-CDR). We avoid tasks that depend on poorly annotated, sparsely populated, or subjectively scored TCGA fields.

4. **Acknowledge transfer validity limits honestly.** Each task includes a "Transfer validity risk" note assessing whether the single-cell → bulk → label chain is likely to hold. Tasks with known fragilities (low prevalence labels, small cohorts, indirect proxies) are flagged so results can be interpreted accordingly.

5. **Cover multiple evidence modalities per cancer type.** Where possible, each cancer has at least one molecular (DNA/protein-grounded), one pathology (histology-grounded), and one clinical (outcome-grounded) task. This ensures the benchmark tests different facets of biological validity, not just one axis repackaged.

6. **Pan-cancer tasks test universal biology.** CNA dosage coupling, cell cycle, chromosomal instability, purity confounding, and epigenetic silencing are axes that should appear in every cancer type. These tasks aggregate across cancer types and test whether programs capture pan-cancer phenomena.

## Validation Framework

All tasks produce a **ranked list of K cNMF tumor-compartment programs**. Ranking quality is evaluated by two-tier validation in TCGA:

- **Tier 1 (bulk RNA-seq — direct activity scoring)**: Compute program activity per TCGA sample using single-sample GSEA (ssGSEA) of the program gene list against log₁p(TPM+1) expression. ssGSEA normalizes for gene-set size, making scores comparable across programs of different sizes. Score each program by its association with the target variable. Spearman ρ between discovery-derived ranking and TCGA-derived ranking = benchmark score.
- **Tier 2 (label-orthogonal enrichment)**: The grouping label comes from a non-transcriptomic source (DNA mutation, protein IHC, pathologist grading, clinical endpoint), but the scoring mechanism is still RNA-based — this tier tests whether program gene sets enrich in condition-stratified DE, not whether the programs transfer to a different assay.
  - *Molecular tasks*: DE in TCGA bulk RNA-seq between molecular subgroups (mutation-present vs absent, amplified vs non-amplified). Rank programs by GSEA-preranked enrichment score in the DE gene list.
  - *Pathology tasks*: DE between pathology-positive vs pathology-negative TCGA samples. Rank programs by enrichment score in the DE gene list.
  - *Clinical tasks*: DE between clinical endpoint groups. **For survival/time-to-event endpoints**, restrict to uncensored events (event indicator = 1) when computing quartiles, or use Cox PH univariate z-score as the program-level score. Do not use raw time-to-event quartiles without filtering for censoring.

### Scoring Notes

**Program activity scoring**: Use ssGSEA (Barbie et al. 2009) rather than mean z-score to compute per-sample program activity. This accounts for differences in program gene-set size — a 10-gene and 200-gene program produce comparable scores. If ssGSEA is unavailable, use mean z-score but report program size alongside results.

**Prevalence threshold**: If a binary label has >80% prevalence in the positive class (or <20%), the binary test is underpowered. In this case: (1) switch to a continuous surrogate variable if available (specified per task), (2) report the prevalence and flag the result as low-confidence, or (3) skip the tier. Each task with a known prevalence risk specifies its fallback.

**Censoring in clinical tasks**: Time-to-event variables (OS.time, PFI.time, DFI.time) are right-censored. When stratifying into quartiles, use only uncensored observations (OS=1, PFI=1, DFI=1) to define the quartile boundaries, then assign all samples to quartiles. Alternatively, score each program by Cox PH univariate z-score (program activity as sole covariate, time-to-event as outcome). Report which method was used.

**Expected Spearman ρ ranges**: Interpret benchmark scores using these approximate ranges (based on transfer validity assessment per task):
- **Strong transfer** (ρ > 0.5): Tasks with large-effect-size binary axes and mechanistic grounding (e.g., ER status, BRAF V600E, MSI-H, HPV status, squamous vs glandular).
- **Moderate transfer** (ρ 0.3–0.5): Tasks with continuous variables, moderate effect sizes, or indirect proxies (e.g., nuclear grade, CNA dosage coupling, survival endpoints).
- **Weak transfer** (ρ < 0.3): Tasks with low-prevalence labels, small cohorts, or conceptually indirect validation (e.g., epigenetic silencing, purity confounding, perineural invasion).
These are calibration guides, not pass/fail thresholds. A task achieving ρ = 0.25 in the "weak" category may still be informative.

**Intra-cancer task correlation**: Tasks within the same cancer type often share variance. For example, in BRCA, ER status (B1), HER2 (B2), and grade (B3) are biologically correlated — a single cNMF program may rank highly for multiple tasks. When interpreting per-cancer results, report the Spearman correlation matrix of program rankings across tasks within each cancer type to identify shared vs independent axes. A program ranking #1 for three correlated tasks represents one validated axis, not three.

### Task Flags

- **[Exploratory]**: Tasks with known power limitations (small N, high prevalence, sparse labels). Results should be reported with wide confidence intervals and interpreted cautiously.
- Tasks not flagged as exploratory are expected to produce interpretable benchmark scores.

## Common File Paths

| Resource | Path |
|---|---|
| Bulk RNA-seq | `data/molecular/{cancer}_tcga_gdc/data_mrna_seq_tpm.txt` |
| Somatic mutations | `data/molecular/{cancer}_tcga_gdc/data_mutations.txt` |
| Copy number (GISTIC) | `data/molecular/{cancer}_tcga_gdc/data_cna.txt` |
| Sample metadata | `data/molecular/{cancer}_tcga_gdc/data_clinical_sample.txt` |
| Pathology reports | `results/path_reports/{cancer}_tcga_gdc_extracted.jsonl` |
| Clinical endpoints (primary) | `data/clinical/TCGA-CDR.csv` |
| Clinical endpoints (extra) | `data/clinical/ExtraEndpoints.csv` |

**Barcode linking**: Patient barcode = first 12 characters of sample barcode (e.g., `TCGA-A1-A0SK`). Pathology JSONL `patient_filename` = `TCGA-XX-XXXX.UUID`; use prefix before the period. TCGA-CDR uses `bcr_patient_barcode` directly.  
**Primary tumor filter**: Sample barcode character 14 = `1` (e.g., `-01A`) indicates primary tumor.

## Task Index

| File | Cancer | ID | Task | Category | Tier 2 label source | Flag |
|---|---|---|---|---|---|---|
| [brca.md](brca.md) | BRCA | B1 | ER+ Luminal Identity | Molecular | ER IHC (PANCAN followup, 96%) | |
| [brca.md](brca.md) | BRCA | B2 | HER2 Amplification | Molecular | ERBB2 CNA ≥ 2 | |
| [brca.md](brca.md) | BRCA | B3 | Invasive Lobular / CDH1-Loss | Pathology | `histologic_type` + CDH1 mutation (13%) | |
| [brca.md](brca.md) | BRCA | B4 | Mitotic / Proliferative | Pathology | `nottingham_mitotic_score` (N=600) | |
| [ccrcc.md](ccrcc.md) | CCRCC | C1 | VHL-Loss / HIF Hypoxia | Molecular | VHL mutation | |
| [ccrcc.md](ccrcc.md) | CCRCC | C2 | Sarcomatoid Dedifferentiation | Pathology | `sarcomatoid_differentiation` | |
| [ccrcc.md](ccrcc.md) | CCRCC | C3 | BAP1-Loss Dedifferentiation | Molecular | BAP1 mutation (11%) | |
| [gbm.md](gbm.md) | GBM | G1 | Mesenchymal Subtype | Molecular | NF1 mutation | |
| [gbm.md](gbm.md) | GBM | G2 | Pseudopalisading Necrosis | Pathology | `palisading_necrosis` | |
| [gbm.md](gbm.md) | GBM | G3 | MGMT / Survival | Clinical | `OS.time` (TCGA-CDR, uncensored) | |
| [gbm.md](gbm.md) | GBM | G4 | EGFR-Amplified / Classical | Molecular | EGFR mutation (23%) | |
| [gbm.md](gbm.md) | GBM | G5 | Ki-67 Proliferation | Pathology | `ki67_percent` (continuous, N=170) | |
| [hgsoc.md](hgsoc.md) | HGSOC | H1 | HRD Program | Molecular | BRCA1/2 mutation | |
| [hgsoc.md](hgsoc.md) | HGSOC | H2 | Platinum Response | Clinical | `PFI.time` (TCGA-CDR, uncensored) | |
| [hgsoc.md](hgsoc.md) | HGSOC | H3 | CCNE1-Amplified Proliferative | Molecular | CCNE1 CNA ≥ 2 (19%) | |
| [hnsc.md](hnsc.md) | HNSC | HN1 | HPV-Positive Program | Molecular | `p16_status` / TP53 absence | |
| [hnsc.md](hnsc.md) | HNSC | HN2 | Extracapsular Nodal Extension | Pathology | `extranodal_extension` | |
| [hnsc.md](hnsc.md) | HNSC | HN3 | Depth of Invasion | Pathology | `depth_of_invasion_mm` (continuous) | |
| [hnsc.md](hnsc.md) | HNSC | HN4 | Perineural Invasion | Pathology | `perineural_invasion` (52%, N=358) | |
| [paad.md](paad.md) | PAAD | PA1a | Classical Subtype | Molecular | GATA6 mRNA + SMAD4 wildtype | |
| [paad.md](paad.md) | PAAD | PA1b | Basal-Like Subtype | Molecular | KRT17 mRNA + SMAD4 mutation | |
| [ucec.md](ucec.md) | UCEC | U1 | POLE Ultramutator | Molecular | POLE hotspot mutation | |
| [ucec.md](ucec.md) | UCEC | U2 | Serous vs Endometrioid | Pathology | `histologic_type` | |
| [ucec.md](ucec.md) | UCEC | U3 | Deep Myometrial Invasion | Pathology | `myometrial_invasion_over_50pct` | |
| [ucec.md](ucec.md) | UCEC | U4 | CTNNB1-Mutant / WNT-Activated | Molecular | CTNNB1 mutation (27%) | |
| [coadread.md](coadread.md) | COADREAD | CR1 | MSI-H Program | Molecular | `mmr_status` / mutation count | |
| [coadread.md](coadread.md) | COADREAD | CR2 | Mucinous Histology | Pathology | `mucinous_component` | |
| [coadread.md](coadread.md) | COADREAD | CR3 | Neoadjuvant CRT Response (READ) | Clinical | `DFI.time` (TCGA-CDR, uncensored) | Exploratory |
| [coadread.md](coadread.md) | COADREAD | CR4 | BRAF V600E / Serrated Pathway | Molecular | BRAF V600E mutation (14%) | |
| [skcm.md](skcm.md) | SKCM | SK1 | BRAF V600E Program | Molecular | BRAF V600E mutation | |
| [skcm.md](skcm.md) | SKCM | SK2a | MITF-High Proliferative | Molecular | MITF mRNA + BRAF V600E mutation | |
| [skcm.md](skcm.md) | SKCM | SK2b | MITF-Low Invasive | Molecular | AXL mRNA + NF1 mutation | |
| [skcm.md](skcm.md) | SKCM | SK3 | Breslow Thickness | Pathology | `breslow_thickness_mm` | Exploratory |
| [cesc.md](cesc.md) | CESC | CE1a | Squamous Differentiation | Pathology | `histologic_type` (squamous) | |
| [cesc.md](cesc.md) | CESC | CE1b | Glandular Differentiation | Pathology | `histologic_type` (adenocarcinoma) | |
| [cesc.md](cesc.md) | CESC | CE2 | PIK3CA-Mutant / PI3K-Activated | Molecular | PIK3CA mutation (28%) | |

| [pancancer.md](pancancer.md) | All | PC1 | Epigenetic Silencing | Molecular | CNA-residual expression + EZH2/DNMT3A mutation | |
| [pancancer.md](pancancer.md) | All | PC2 | CNA Dosage Coupling | Molecular | Per-gene CNA-expression Pearson r + seg CNA | |
| [pancancer.md](pancancer.md) | All | PC3 | Chromosomal Instability Response | Molecular | Fraction genome altered (FGA from seg file) | |
| [pancancer.md](pancancer.md) | All | PC4 | Histologic Grade | Pathology | `histologic_grade` (ordinal, per cancer) | |
| [pancancer.md](pancancer.md) | All | PC5 | Lymphovascular Invasion | Pathology | `lymphovascular_invasion` (per cancer) | |
| [pancancer.md](pancancer.md) | All | PC6 | Disease-Specific / Overall Survival | Clinical | DSS/OS (Cox PH, cancers with ≥20% events) | |

**Total: 42 tasks — 36 cancer-type-specific + 6 pan-cancer (applied per cancer type, aggregated)**
