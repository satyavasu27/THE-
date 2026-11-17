# Dataset source audit and acquisition gate

## Binding rule

At least 2,000 unique, non-duplicate, valid original records are required in **each** selected dataset, after applying the prespecified cohort restriction and before any resampling. The published/source count is not an independently audited file count. A candidate is not accepted until the original file is available locally and `scripts/audit_dataset.py` records its row count, duplicate count, target missingness, labels, and checksum.

| Requirement | Candidate 1: ARMD urine-culture subset | Candidate 2: Taylor et al. ED minimal dataset |
|---|---|---|
| Repository / primary reference | Dryad dataset DOI 10.5061/dryad.jq2bvq8kp; descriptor paper in *Scientific Data* (2025) | PLOS ONE article DOI 10.1371/journal.pone.0194085; S1 CSV supplement DOI 10.1371/journal.pone.0194085.s001 |
| Source-published size | 751,075 total cultures across urine, blood, and respiratory in the dataset descriptor; urine is reported as about 50%. Exact urine-only row count must be computed from cohort.csv. | 80,387 adult ED visits in the original publication; 18,284 positive and 62,103 negative culture outcomes reported. The CSV file must be independently counted after download. |
| Minimum required | 2,000 urine-only unique valid rows | 2,000 unique valid visit rows |
| Target | `was_positive` (organism identified) after selecting urine cultures; not a symptom-adjudicated UTI label | Paper-defined culture/UTI proxy for symptomatic ED encounters; inspect the data dictionary and code before assigning a binary label. |
| Candidate features | Culture type, organism/positivity, linked demographics, clinical and temporal context in separate tables. Only predictors known by prediction time may be joined. | Demographics, symptoms/physical exam, vital signs, labs, urinalysis, medical history and visit-level data described in the paper. |
| Positive / negative counts | Not independently measured locally. Do not infer urine-only counts from the global all-culture total. | Paper reports 18,284 / 62,103; file-level counts and duplicate assessment pending. |
| Missing / duplicates | Pending file inspection and join audit. Avoid multiplying culture rows in one-to-many joins. | Pending file inspection. Repeated patients exist in the cohort; patient IDs, if present, must drive grouped splitting. |
| Licensing / access | Publicly deposited in Dryad; use repository license and data-use notes shown with the version. Files total about 24 GB; download only required source tables and keep raw files out of Git. | Public supplementary data linked by the PLOS ONE article; record license from source before redistribution. The S1 CSV is described as about 81.7 MB. |
| Direct source | https://datadryad.org/dataset/doi:10.5061/dryad.jq2bvq8kp | https://doi.org/10.1371/journal.pone.0194085.s001 |
| Local file present? | No | No |
| Accepted now? | **No — provisional source candidate only** | **No — provisional source candidate only** |

## Compatibility and clinical interpretation

These sources do **not** share a demonstrated identical target. ARMD's `was_positive` denotes organism identification in a urine culture specimen in an AMR EHR cohort; it is not a clinical UTI diagnosis and does not itself guarantee symptoms or a harmonized colony-count threshold. The Taylor ED dataset uses an emergency-visit cohort with urinary symptoms and a paper-defined culture/UTI proxy. Their populations, sampling frame, and label construction differ. Do not pool records, infer a common clinical UTI label, or interpret cross-dataset score differences as a clean external validation until the exact target codes and thresholds have been inspected and harmonization is defensible. If target definitions cannot be aligned, report independent tasks and mark direct cross-dataset comparison as not valid.

## Rejected or unsuitable candidates from the search

| Candidate | Published size / label | Decision |
|---|---|---|
| Rodare / Liou et al. clinical microscopy images | 300 patient images and 3,562 object annotations; segmentation classes, no patient-level positive/negative culture label | Reject for this cohort task: fewer than 2,000 patient records and no binary urine-culture target. Object annotations do not count as independent patients. |
| Mendeley clinical urine-culture Petri-dish image set | 1,500 plates (498 positive, 500 negative, 502 uncertain) | Reject: below the strict 2,000 original-observation minimum. Do not pad or augment to qualify. |
| Mendeley point-of-care urinalysis-interface dataset | 63,279 urinalyses reported, but target is interface/reporting accuracy, not UTI or culture outcome | Reject for the selected endpoint: row count alone does not make a UTI-prediction dataset. |
| Small classic urine chemistry datasets (e.g., urine analysis benchmark) | Dozens of records | Reject: below minimum and not a large culture-positive cohort. |

## Acquisition result

As of 2026-11-17 neither original file has been acquired into this workspace. The shell can reach GitHub, but direct TLS access to Dryad failed and the primary downloadable endpoints are outside the environment's allowed shell hosts. Therefore, the reported source sample sizes are evidence supporting candidates, not actual local measurements. The strict minimum-row dataset gate has not passed and final experiments are prohibited at this stage.

## Planned data integrity steps after availability

1. Save the original source file unchanged, record version/date/license/URL and SHA-256, and never commit restricted or large raw data.
2. Parse the file without dropping rows. Report total original rows, target missingness, exact urine-only count, exact unique count, exact duplicate rows and repeated patient IDs.
3. Determine the analytic unit (patient visit vs culture specimen) and pre-specify de-duplication. Do not blindly drop repeated encounters if they are legitimate; prevent patient leakage with grouped splitting.
4. Report exclusions and valid records before/after cleaning, positive/negative counts, field types, missingness and unit-of-analysis concerns.
5. Reject a dataset if its final valid, unique original observations are below 2,000.
6. Treat one-to-many joins as potential row multiplication; assert the expected culture key cardinality before and after merges.
7. Only after acceptance, construct independent EDA notebooks and paper-specific train/validation/test pipelines.
