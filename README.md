# UTI Machine-Learning Research Workspace

**Project:** Machine Learning-Based Urinary Tract Infection Detection: Comparative Evaluation of Recent Methodologies, Dataset Analysis, and Research Gap Identification.

**Status (2026-11-17):** Phase 1 workspace audit and source verification started; no legacy research files or datasets were present in the checkout. Two large public-data candidates have been verified from their primary sources, but neither file has been downloaded into this restricted execution environment. The dataset acquisition/row-audit gate is therefore **not passed**. No model experiments or quantitative results are claimed. See [`docs/EXECUTION_STATUS.md`](docs/EXECUTION_STATUS.md).

## Research-integrity gate

The project must not run comparative experiments until both local datasets have been acquired and audited for (a) at least 2,000 unique, valid original records each, (b) non-ambiguous target definitions, (c) duplicate and missingness counts, and (d) outcome counts after the urine-only restriction where relevant. The candidate sources are documented in [`data/README.md`](data/README.md). Their outcomes are not assumed to be equivalent and must not be pooled.

## Layout

- `data/` — source manifest, raw-data landing area, processed-data landing area.
- `literature/` — verified review table and research-gap analysis.
- `src/uti_research/` — reusable methodology and evaluation code.
- `scripts/` — command-line entry points.
- `configs/` — method profiles and run settings.
- `notebooks/` — unexecuted per-dataset EDA notebook template; run separately after data acquisition.
- `results/` — reserved for genuine results only; currently no experiment outputs.
- `logs/` — experiment and acquisition logs.

## Installation / verification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

A reproducibility scaffolding and explicit stop gate are present. The current runner keeps imputation/encoding/scaling within the training pipeline but does **not yet implement each paper's complete feature-selection/tuning protocol**; it is not a completed reproduction. No model output should be reported until real source files have been acquired, audited and compatible paper-specific pipelines completed. For data that the source license permits, place unmodified copies in `data/raw/`; record the exact version, URL, retrieval date, checksum, and license in the manifest. Do not commit protected or large clinical data.
