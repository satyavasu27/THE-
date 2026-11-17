# Research presentation (progress version; not a results presentation)

## Slide 1 — Title and status
Machine Learning-Based UTI Detection: Comparative Evaluation of Recent Methodologies, Dataset Analysis, and Research Gap Identification. Status: source audit and literature scoping; no experiments yet.

## Slide 2 — Clinical framing
Differentiate symptomatic clinical UTI from urine-culture positivity. Positive culture alone may also reflect asymptomatic bacteriuria, colonization or contamination. A prediction model is decision support, not a diagnosis.

## Slide 3 — Data gate
Two high-volume public source candidates: ARMD (Dryad; 751,075 total microbiology cultures, urine approx. half) and Taylor et al. S1 CSV (80,387 adult ED visits, source paper's culture/UTI proxy). Local files not acquired, exact deduplicated urine counts pending; both currently rejected/not accepted for modeling.

## Slide 4 — Dataset compatibility
ARMD is a microbiology/AMR culture cohort; Taylor is an ED symptomatic-context cohort with a paper-defined proxy label. Sample units, thresholds and clinical target may differ. No pooling or direct cross-dataset interpretation before label audit.

## Slide 5 — Literature evidence (2024–2026)
2023 Seheult et al.: multisite decision-tree screening; held-out NPV >90% and false-negative proportion under 5% in its low-risk triage framing. 2024 Dedeene et al.: MLP AUROC .884; six-variable flow-cytometry MLR .858. 2025 Farashi & Momtaz: feature-reduced ensemble on Taylor data; reported AUC 88.53/100, accuracy 85.64%. 2026 Lin et al.: pediatric RF AUROC .814, sensitivity .770 in small internal holdout. 2026 Wasfy et al.: CatBoost AUROC .858 with sensitivity .587 in sample-level internal test.

## Slide 6 — Defensible research gaps
Outcome mismatch, patient-level leakage risk, limited external validation, threshold-dependent false negatives, calibration and subgroup transport. These are provisional evidence-based gaps, not proven novel contributions.

## Slide 7 — Planned reproducible evaluation
Prespecified train/validation/test split; patient grouping when available; train-only feature selection; validation-only threshold selection; full sensitivity/specificity/PPV/NPV/FNR/AUROC/PR-AUC, calibration, Brier, bootstrap CIs and error review.

## Slide 8 — Current blockers and next steps
Data hosts are outside the sandbox's shell egress allowlist; no local data means no valid EDA or results. Make the original files accessible, verify >=2,000 original valid records per dataset, then run the code and replace this progress deck with findings.

**Important:** this is deliberately a progress outline, not a fabricated presentation of results.
