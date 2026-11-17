# Machine Learning-Based Urinary Tract Infection Detection
## Comparative Evaluation of Recent Methodologies, Dataset Analysis, and Research Gap Identification

**Progress report, not a completed experimental manuscript**  
**Date:** 17 November 2026  
**Research status:** data acquisition blocked; no model results available

---

## Abstract

This project is designed to compare recent machine-learning approaches to urinary tract infection (UTI) and urine-culture outcome prediction using two large, independently sourced datasets, with patient-level validation, clinically oriented metrics and explicit target-definition controls. The initial repository audit found no prior UTI files or datasets. Source discovery identified a large public antibiotic-resistance microbiology dataset (ARMD) from Dryad and the Taylor et al. emergency-department (ED) dataset distributed as a PLOS ONE supplement. The source descriptions report cohorts far above the required 2,000 observations, but their original files could not be downloaded into this workspace because the shell environment cannot access the relevant repository hosts. Neither dataset has therefore been locally counted, deduplicated, inspected, or accepted for modeling. This is a strict stop condition: no experimental results, EDA plots, or comparative claims are reported. A verified seed literature review documents 2024–2026 journal work, including a 2024 flow-cytometry logistic-regression/MLP support tool, a 2025 feature-reduced ED ensemble, and a 2026 pediatric seven-feature random forest. The paper-reported results are distinguished from this project's unrun experiments. Provisional gaps include outcome mismatch, patient-level leakage, limited external validation, sensitivity/threshold trade-offs, and insufficient calibration/utility evaluation. Reproducible audit, modeling and evaluation scaffolding is present; the final study requires access to both primary source files and subsequent independent audit.

**Keywords:** urinary tract infection; urine culture; machine learning; clinical decision support; external validation; sensitivity; calibration; data leakage.

## 1. Introduction and motivation

Urine culture is used to identify microbial growth, while clinical UTI assessment requires clinical context and interpretation. Culture positivity alone may represent symptomatic infection, asymptomatic bacteriuria, colonization, contamination or another state. A classifier trained on a culture label should therefore be described as predicting that source's culture outcome, not diagnosing UTI. The distinction is central to label quality, threshold selection and clinical interpretation.

Recent research studies routine urinalysis, blood tests, demographic/contextual data and advanced ML to estimate urine-culture results or UTI-related outcomes. Potential uses include prioritizing specimens for review or supporting risk estimates before culture finalization. The clinical cost of missed positive cases makes sensitivity and false-negative analysis important; unnecessary tests and treatment make specificity and predictive values important too. AUC or accuracy alone is not sufficient.

## 2. Problem statement and objectives

The intended experiment would compare three traceable recent methodologies on two independently sourced datasets with at least 2,000 unique valid original observations each. Preprocessing, feature selection and threshold selection must be performed without test leakage. Patient grouping is required where identifiers exist. Dataset-specific labels must be retained when their clinical definitions cannot be harmonized.

The current deliverable satisfies the initial workspace audit, source discovery, seed literature verification and reproducible-code scaffolding. It does **not** satisfy the dataset-acquisition, EDA, model-training, performance-analysis or final-presentation completion criteria.

## 3. Dataset audit and size gate

### 3.1 Candidate source 1: ARMD (Dryad)

ARMD is a de-identified Stanford Health Care EHR dataset with microbiology culture, organism, positivity, susceptibility and linked clinical/demographic context. The descriptor reports 751,075 total microbiology culture records from 283,715 unique patients, with urine cultures approximately half of all specimens. The relevant culture table's `was_positive` field means an organism was identified. The source is large enough to be a plausible >=2,000 urine-culture candidate, but the exact urine-only count, duplicates, class counts, missingness and target details must be measured from the cohort CSV after source filtering. It is not a symptom-adjudicated UTI outcome.

### 3.2 Candidate source 2: Taylor et al. ED minimum dataset

The original PLOS ONE paper describes 80,387 adult ED visits from four EDs with urine culture results and symptoms potentially attributable to UTI. The source paper reports 18,284 positive cultures and 62,103 negative cultures and links an 81.7 MB minimal CSV supplement. The cohort is a plausible >2,000 source, but the file's row count, exact label mapping, patient identifier availability, missingness and duplicate sample/visit records remain unverified locally. Its clinical/context definition differs from ARMD's general culture-positive flag.

### 3.3 Required verification table

| Requirement | Candidate 1: ARMD | Candidate 2: Taylor ED CSV |
|---|---|---|
| Original source-published row count | 751,075 across all culture types; urine subset exact count pending | 80,387 ED visits in the paper |
| Valid records after local cleaning | Not measured; file unavailable | Not measured; file unavailable |
| Minimum required | 2,000 unique valid urine-culture records | 2,000 unique valid ED records |
| Target | `was_positive` after urine-only filter; culture organism identified | Paper-defined culture/UTI proxy; exact code and threshold need source-code verification |
| Positive / negative | Not measured for urine-only subset | Paper: 18,284 / 62,103; local confirmation pending |
| Duplicates / repeated patients | Pending local key and join audit | Pending local file audit; patient-level grouping required if ID present |
| Verified source | [Dryad DOI](https://doi.org/10.5061/dryad.jq2bvq8kp) | [PLOS supplement DOI](https://doi.org/10.1371/journal.pone.0194085.s001) |
| Accepted? | **No — candidate only; original file absent** | **No — candidate only; original file absent** |

Source-published counts are not locally observed counts. This distinction is why neither candidate is marked accepted. No data are combined. If the target definitions cannot be aligned after inspection, cross-dataset results will be presented as distinct tasks rather than a shared external-validation comparison.

## 4. Data access, quality and EDA status

No source data files were in the repository. Direct TLS retrieval from Dryad failed from the shell; the sandbox's outbound shell hosts do not include Dryad, PLOS/PMC or the source supplementary-file repository. The source data are not copied into GitHub project repositories. Consequently, the requested data types, feature dictionaries, missing values, exact duplicate rows, conflicting record IDs, valid record counts, and class distributions cannot be truthfully reported here.

The EDA notebook at `notebooks/01_dataset_eda_template.ipynb` is an unexecuted template for each source separately. It includes source-level row/label/missingness checks, class-distribution plotting, missing-value heatmaps, numeric correlation and distributions, categorical frequency plots, and positive-vs-negative comparisons. No visualizations are generated in this report because there are no observations to visualize.

## 5. Literature review (2023–2026): verified seed evidence

This is a verified seed review, not a completed systematic review. Each entry is checked against a journal or data-repository record. The details and citations are also in `literature/review.md` and `literature/papers.csv`.

### 5.1 2023: Seheult et al.

The 2023 PittUDT paper evaluated a recursive-partitioning decision tree for urine-culture positivity using paired macroscopic and microscopic UA. The training data included 19,511 paired samples and the held-out test set 9,773 samples across five hospitals. It reports test NPV above 90%, a 30–60% negative group for potential reflex triage, and a false-negative proportion under 5% in its low-risk screening framing. WBC, leukocyte esterase and bacteria had individual AUROCs of 0.79, 0.78 and 0.77. This is a clinically relevant example of prioritizing NPV/false negatives over overall accuracy. Its endpoint is still culture positivity, and local historical test protocols limit transportability.

### 5.2 2024: Dedeene et al.

Dedeene et al. evaluated a rapid culture-result prediction tool in a Belgian hospital network. The data included 34,584 training samples and time-separated test sets of 10,083 and 9,289. A six-flow-cytometry-variable multiple logistic regression achieved AUROC 0.858 (95% CI 0.852–0.865); an MLP achieved AUROC 0.884 (95% CI 0.878–0.890). They also proposed likelihood-ratio risk bands and ongoing quality control. Their endpoint is urine culture positivity rather than symptom-confirmed UTI. The particular analyzer inputs limit transport to datasets with different measurement methods.

### 5.3 2025: Farashi and Momtaz

This study reanalyzed the Taylor ED cohort with feature-reduction approaches. A 211-feature source space was reduced using manual exclusion, filter and embedded feature-selection methods, followed by wrapper selection. The final 18-feature set included urinalysis (nitrite, WBC, bilirubin, leukocyte, urobilinogen, blood, clarity, color), medication/history, age, chief complaint, gender and blood variables. Their equal-weight DT/XGBoost/LightGBM voting classifier reported AUC 88.53/100 and accuracy 85.64%. The cohort is not independent of the Taylor source dataset. Any reproduction must repeat feature selection within training data only; full-source feature selection before test splitting would leak information.

### 5.4 2025: Sergounioti et al.

An 8,065-record single-laboratory study predicted culture positivity at >10^5 CFU/mL using routine urinalysis and demographics. It compared RF, XGBoost, Extra Trees, voting and stacking under stratified 10-fold CV. XGBoost AUROC was 0.819; threshold optimization was reported to increase sensitivity from 70.2% to 87.9% with NPV 96.4%. The source data are not public and the cohort lacks symptom variables, so this result is contextual evidence rather than a reproducible project baseline.

### 5.5 2026: Lin et al.

A single pediatric hospital cohort contained 581 suspected-UTI samples (245 positive, 336 negative); a stratified 70:30 split created an internal validation cohort of 175. Variable selection combined univariate analysis, LASSO and RFE, followed by clinically guided selection of gender, absolute lymphocyte count, CRP, leukocyte esterase, nitrite, urinary bacteria count and urinary WBC count. RF achieved validation AUROC 0.814 (95% CI 0.742–0.875) and sensitivity 0.770 (95% CI 0.662–0.865). The small single-center validation cohort, particularly 74 positive validation cases, limits precision and transportability.

### 5.6 2026: Wasfy et al.

A multicenter-source sample-record cohort of 2,530 paired UA/culture records was split randomly at the sample level. The positive label count was 715; repeated file IDs were reported (2,294 distinct among 2,529 records with IDs). CatBoost's test AUROC was 0.858 (95% CI 0.829–0.892), while sensitivity was 0.587. The sample-level split could allow repeated-patient leakage; centre/date identifiers were unavailable. The findings illustrate that high AUROC does not by itself establish a safe rule-out strategy.

### 5.7 Related dataset sources

Liou et al.'s 2024 open urine microscopy data descriptor offers 300 images from 300 symptomatic patients and 3,562 annotated objects for segmentation/object recognition. It does not meet the project's 2,000 patient-record floor and does not provide a binary culture outcome; it was rejected for this tabular cohort task. The ARMD paper reports 751,075 total mixed-site cultures; it remains a candidate pending exact urine-only file audit. Taylor et al.'s 2018 paper is outside the requested recent-paper window but provides a publicly linked large supplemental dataset used by later methodology work.

## 6. Evidence-based research gaps

1. **Outcome definition and label transport:** reviewed work alternates between culture positivity, bacteriuria and clinical UTI. Positive culture is not equivalent to clinical infection; thresholds and symptom context differ.
2. **Patient/site/time leakage and external validation:** random record splits can put repeated samples from the same patient in train and test. Several recent cohorts use one institution or internal random validation.
3. **Sensitivity and rule-out:** Wasfy et al. report AUROC 0.858 but sensitivity 0.587, a poor rule-out operating point. Other work shows threshold changes can shift sensitivity markedly; thresholds must match purpose.
4. **Calibration and decision utility:** discrimination metrics alone do not measure probability reliability or net clinical benefit. Calibration and decision curves are required where a specific downstream decision and harm/benefit thresholds are defensible.
5. **Interpretability and subgroup generalization:** feature attribution (e.g., SHAP) can explain associations in a model but cannot establish causal effects or solve domain shift. Small subgroups make subgroup metrics uncertain.
6. **Reproducibility and open-data access:** many hospital studies do not release row-level data, which limits independent reproduction and external validation.

The full gap matrix is in `literature/research_gaps.md`. These are evidence-grounded directions, not proof of novelty.

## 7. Proposed methodology and partial implementations

The requested full factorial comparison is represented by six slots in `configs/experiment_matrix.json`: each of the three selected paper families paired with each of the two dataset candidates. `scripts/run_matrix.py` audits and optionally executes only combinations whose source file, target mapping, row count, record uniqueness, and exact dataset-specific feature mapping have been verified. The dry run performed for this update reported **6/6 blocked because source files are missing**. This is not six model executions and does not produce scientific performance results.

### 7.1 Candidate paper-specific implementations

- **2024 Dedeene limited-feature MLR:** use only the six same-definition flow-cytometry variables (RBC, WBC, bacteria, yeast, tubular epithelial, squamous epithelial counts). Do not substitute dipstick or unrelated microscopy counts without an explicit deviation. The target must use compatible source culture criteria. On datasets without exact analyzer measurements, mark not evaluable.
- **2025 Farashi voting ensemble:** use the reported 18-feature set and an equal-weight DT/XGBoost/LightGBM ensemble. Re-run all feature selection/tuning within training folds. This paper reused Taylor data, so reanalysis of Taylor is not independent validation. The current scaffold's soft-voting choice is a disclosed adaptation unless the original exact voting semantics are verified.
- **2026 Lin seven-feature RF:** use the reported seven routine markers, with class weighting, and train-only feature processing. Applying a pediatric-source method to adult data is out-of-domain adaptation, not direct replication. The source article's precise RF settings must be extracted before exact reproduction claims.

Code is in `src/uti_research/` and `scripts/run_experiment.py`. It refuses to run without an explicit `--approved` flag. The input data, label mapping, features and published hyperparameters have not been validated because the files are not present; therefore, this code is **methodology scaffolding**, not a completed implementation result.

### 7.2 Split and leakage controls planned

Use a patient-grouped split where identifiers exist. Candidate design is approximately 60% training, 20% validation and 20% held-out test with stratification/grouping where feasible; this is a project design, not claimed to reproduce the source papers. The current runner places imputation, encoding and (for MLR) scaling inside a training-fitted pipeline. It does not yet implement Farashi's full multi-stage feature selection or a nested search for paper-specific hyperparameters; therefore it must not be presented as a full reproduction. These components must be implemented inside the training folds before any final comparison. Select an operating threshold on validation only. A sealed test set is used once for final metrics. If no patient IDs are available, state the residual leakage risk and avoid patient-independence claims.

## 8. Evaluation criteria and rationale

The executed pipeline is intended to report train, validation and test data separately:

- **Accuracy:** overall fraction correct, but can obscure minority-class errors.
- **Sensitivity/recall and false-negative rate:** proportion of positive labels found / missed; important for evaluating screening or rule-out harms.
- **Specificity and false-positive rate:** ability to avoid flagging negative cultures; relevant to unnecessary follow-up/testing.
- **PPV/precision and NPV:** predictive values at observed prevalence; prevalence dependent and not portable without recalibration.
- **F1 and balanced accuracy:** summarize precision/recall and class-balanced correctness, but do not replace the confusion matrix.
- **AUROC and PR-AUC (average precision):** ranking performance; PR-AUC is more informative when positive prevalence is low. Neither selects a clinically appropriate threshold.
- **Sensitivity at fixed specificity / specificity at fixed sensitivity:** show operating trade-offs. Threshold is selected on validation; final test ROC summaries are descriptive.
- **Brier score and calibration plot:** assess probability quality; a well-ranked model may still be poorly calibrated.
- **95% bootstrap CIs:** quantify sampling uncertainty. Planned initial implementation is row-level bootstrap; if repeated records/patients remain, patient-cluster bootstrap is preferable.
- **Statistical comparison:** paired bootstrap AUROC difference on identical held-out observations is implemented as a helper; it cannot be used across nonmatching datasets or outcome definitions.
- **Decision curve analysis:** potentially appropriate only after a specific clinical action and harm/benefit thresholds are stated; no DCA is reported now.

## 9. Results

### 9.1 Actual project experiments

**Not run.** No research data files were acquired. No sample-level experiment outputs exist. The following requested output table is intentionally blank/not reported:

| Model | Dataset | Accuracy | Sensitivity | Specificity | Precision | F1 | NPV | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dedeene-family MLR | — | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured |
| Farashi-family voting ensemble | — | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured |
| Lin-family RF | — | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured |

No ROC, PR, confusion-matrix, calibration, feature-importance, subgroup, or SHAP plots are presented. No model is declared strongest. Reported article metrics in Section 5 are published results only, not this project's training/test performance.

## 10. Qualitative analysis

No project predictions or false negatives/false positives exist to review. Published-source observations are limited to the evidence summarized above: flow-cytometry features support culture prediction in Dedeene's setting; UA markers such as nitrite, WBC and specific gravity were influential in the 2025 Amfissa study; the 2026 pediatric RF emphasized bacterial count, leukocyte esterase, nitrite and urinary WBC; and the 2026 sample-level study's sensitivity demonstrates a potential rule-out limitation. Feature importance is associative and dataset-dependent. No clinical diagnostic claim follows from these papers' culture predictions alone.

## 11. Tentative contribution candidates (not novelty claims)

1. **Leakage-resistant cross-source evaluation:** addresses repeated-patient leakage and dataset shift. Validate with patient grouping and prespecified label harmonization. Baselines: logistic regression, RF, gradient boosting and source-aligned published families. Limitations: target incompatibility and missing identifiers can prevent direct validation. Novelty requires a database search and experiments demonstrating a genuinely new validation design, not merely a new dataset pairing.
2. **Sensitivity-focused, calibrated risk workflow:** select a sensitivity/specificity operating point on validation data, report NPV at the observed prevalence, calibration and decision curves. Baselines include default 0.5 threshold and published threshold strategies. Potential advantage is more clinically transparent trade-offs; limitation is that sensitivity target and acceptable false-positive rate require clinical stakeholder input and calibration is prevalence-dependent.
3. **Interpretable feature-availability comparison:** compare a minimal-UA setting to a broader clinical-data setting only where compatible records exist, using train-only processing and SHAP/permutation stability. Novelty requires demonstrating additional robustness or usable explanations beyond papers that already report feature importance/SHAP; explanation alone is not novelty.

All are tentative until data analysis and a formal novelty search are completed.

## 12. Limitations

- No original research files could be acquired or inspected; dataset counts and source labels are not independently verified locally.
- The literature review is a verified seed sample, not exhaustive and not a systematic review with reproducible database queries and duplicate screening.
- The three paper methods have not been trained. Exact hyperparameters, feature units, source label definitions and the original voting mode need final extraction.
- The candidate project datasets differ in sampling frame and likely label construction. Their outcomes should not be pooled without evidence of compatibility.
- Software tests validate utility behavior only; they do not validate a medical model.
- No clinical deployment, clinical utility, diagnostic benefit or treatment safety claim can be made.

## 13. Reproducibility, environment and execution record

The environment started without pandas, NumPy, scikit-learn, matplotlib, seaborn, xgboost or lightgbm installed. A local ignored `.venv` was created and core analysis dependencies plus XGBoost/LightGBM installed from PyPI for code validation. Automated tests: 3 passed; Python modules compile; EDA notebook JSON parses. These are software checks only, not research experiments. Installed versions at validation: Python 3.11, NumPy 2.4.6, pandas 3.1.1, scikit-learn 1.9.1, matplotlib 3.11.2, seaborn 0.13.2, XGBoost 3.2.0, LightGBM 4.7.0. The `requirements.txt` constrains supported ranges; exact environment lockfile remains future work.

The run-log schema is `logs/experiment_log_template.csv`. No executed research experiment rows have been appended. Original data are not committed to Git.

## 14. Conclusion

The source audit establishes a credible path to two large data sources and the literature review identifies specific, defensible methodological concerns. However, the mandatory two-dataset acquisition and independent row/label/duplicate verification have not been completed, so rigorous comparative experiments cannot start. The scientifically correct conclusion is a blocked research execution—not an efficacy result. Once the primary datasets are available in the workspace, the local audit must determine whether each independently satisfies the >=2,000-row requirement, then EDA, method compatibility, paper-faithful modeling and held-out clinical metric analysis can proceed. Until then, no findings about comparative model performance are justified.

## References (selected)

1. Seheult JN, Stram MN, Contis L, Pontzer RE, Hardy S, Wertz W, Baxter CM, Ondras M, Kip PL, Snyder GM, Pasculle AW. Development, Evaluation, and Multisite Deployment of a Machine Learning Decision Tree Algorithm To Optimize Urinalysis Parameters for Predicting Urine Culture Positivity. *J Clin Microbiol*. 2023;61(6):e00291-23. https://doi.org/10.1128/jcm.00291-23
2. Dedeene L, Van Elslande J, Dewitte J, et al. An artificial intelligence-driven support tool for prediction of urine culture test results. *Clin Chim Acta*. 2024;562:119854. https://doi.org/10.1016/j.cca.2024.119854
3. Farashi S, Momtaz HE. Prediction of urinary tract infection using machine learning methods: a study for finding the most-informative variables. *BMC Med Inform Decis Mak*. 2025;25:13. https://doi.org/10.1186/s12911-024-02819-2
4. Sergounioti A, Rigas D, Zoitopoulos V, Kalles D. From Preliminary Urinalysis to Decision Support: Machine Learning for UTI Prediction in Real-World Laboratory Data. *J Pers Med*. 2025;15(5):200. https://doi.org/10.3390/jpm15050200
5. Lin S, Yao J, Fu Q, et al. Construction and validation of a machine learning model for predicting urine culture positivity in children with suspected urinary tract infections. *Ann Med*. 2026;58(1):2742648. https://doi.org/10.1080/07853890.2026.2742648
6. Wasfy IS, Ahmad J, Elsegeay H, et al. Machine-learning prediction of urine-culture positivity in a multicentre test-ordered cohort: Model development and internal validation. *BJUI Compass*. 2026;7(9):e70280. https://doi.org/10.1002/bco2.70280
7. Liou N, De T, Urbanski A, et al. A clinical microscopy dataset to develop a deep learning diagnostic test for urinary tract infection. *Sci Data*. 2024;11:155. https://doi.org/10.1038/s41597-024-02975-0
8. Taylor RA, Moore CL, Cheung K-H, Brandt C. Predicting urinary tract infections in the emergency department with machine learning. *PLOS ONE*. 2018;13(3):e0194085. https://doi.org/10.1371/journal.pone.0194085
9. Nateghi Haredasht F, Amrollahi F, Maddali MV, et al. Antibiotic Resistance Microbiology Dataset (ARMD): A resource for antimicrobial resistance from EHRs. *Sci Data*. 2025. https://doi.org/10.1038/s41597-025-05649-7; dataset: https://doi.org/10.5061/dryad.jq2bvq8kp
