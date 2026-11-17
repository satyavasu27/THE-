# Progress report — 2026-11-17

## Executive status

**Not complete.** The initial workspace was clean of prior UTI project files. Literature and source discovery have produced two credible large public data candidates and a verified recent-paper seed review. The strict requirement of two locally acquired, independently audited datasets of at least 2,000 unique valid original rows is **not yet met**. No data have been fabricated and no experiments have been run or reported.

## Progress by deliverable

- **Workspace audit:** complete; no previous project or datasets found.
- **Data source discovery:** two candidates identified and described in `data/README.md`: (1) Stanford ARMD Dryad cohort and (2) Taylor et al. PLOS ONE ED supplemental CSV. Their source-published sample sizes exceed 2,000, but local file inspection, row-level verification, target counts, missingness and duplicate counts are pending. Both are currently marked **not accepted**.
- **Dataset EDA:** not run; no source files are available locally.
- **Recent literature:** verified papers from 2024, 2025, and 2026 are in `literature/review.md` and `literature/papers.csv`. Results are explicitly paper-reported, not reproduced. Review is a seed review, not a completed systematic review.
- **Research gaps:** source-grounded provisional table in `literature/research_gaps.md`.
- **Three methodology implementations:** framework profiles and code scaffolding added. Paper-specific feature/target mapping and parameters must be checked against actual data; implementations are not claimed as reproductions yet.
- **Evaluation:** generic clinical metric, validation-threshold, bootstrap-CI and curve code is present. Not executed on research data; no confusion matrices or numerical results exist.
- **Final manuscript/presentation:** a concise progress presentation outline is provided in `docs/presentation_outline.md`. A full academic report remains pending, correctly, until the experiment results exist.

## Why the work stopped at the acquisition gate

Primary source files are hosted on Dryad/PLOS supplementary data hosts, which this sandbox cannot access from the shell (outbound shell access is constrained to GitHub, npm and PyPI; Dryad TLS download attempt failed). The GitHub-accessible project contains no copies of the source datasets. There were no local files to audit. Starting experiments without the original data would violate the explicit 2,000-row rule and scientific-integrity instructions.

## Exact next actions

1. Make the primary source datasets available in `data/raw/` or enable direct access to Dryad and the PLOS supplementary-file host.
2. Run `python scripts/audit_dataset.py --input ... --target ... --patient-id ...` for each file, verify target definitions from dictionaries/code, record checksums and accept/reject decisions.
3. Reject any dataset with <2,000 unique valid original rows; never pad or resample to qualify.
4. Confirm the ARMD urine-only denominator, patient linkage, culture label and target missingness; confirm Taylor CSV labels, patient IDs and records against its supplement.
5. Decide whether targets are sufficiently compatible for direct external evaluation. If not, keep endpoints separate and do not claim a shared label.
6. Run notebook EDA for each accepted dataset; only then evaluate feature/method compatibility and run split-safe experiments.
