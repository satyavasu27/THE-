# Six-combination paper × dataset matrix

The requested factorial design is explicitly enumerated in `configs/experiment_matrix.json` and handled by `scripts/run_matrix.py`. This is a three-method × two-dataset matrix, not six independent methodological contributions.

| Combination | Paper family | Dataset candidate | Current state | Scientific compatibility note |
|---|---|---|---|---|
| 1 | Dedeene 2024 limited-feature MLR | ARMD urine subset | **Blocked: source file missing** | Requires exact six flow-cytometry measures and matched units; ARMD feature tables have not been downloaded or inspected. |
| 2 | Farashi 2025 voting ensemble | ARMD urine subset | **Blocked: source file missing** | Paper uses 18 ED/UA/history features from Taylor data; ARMD has a different cohort and no verified matching feature/label mapping. |
| 3 | Lin 2026 seven-feature RF | ARMD urine subset | **Blocked: source file missing** | Requires verified UA/blood analytes and unit mapping; adult ARMD cohort is out-of-domain for the pediatric source model. |
| 4 | Dedeene 2024 limited-feature MLR | Taylor ED S1 | **Blocked: source file missing** | Flow-cytometry assay equivalence is not established; do not substitute ordinary dipstick/microscopy proxies. |
| 5 | Farashi 2025 voting ensemble | Taylor ED S1 | **Blocked: source file missing** | Same source cohort used by the paper; any reproduction on it is not independent external validation. The source S1 feature/target encoding still needs file-level verification. |
| 6 | Lin 2026 seven-feature RF | Taylor ED S1 | **Blocked: source file missing** | Adult ED application is an out-of-domain adaptation; exact analyte availability/units are unverified. |

## Dry-run/execute check

Both `python scripts/run_matrix.py --config configs/experiment_matrix.json` and the guarded `--execute` path were run. All six returned `BLOCKED_DATA_FILE_MISSING`; no model fitting occurred. Dataset mappings for target columns/labels, IDs and dataset-specific input features intentionally remain unset pending file inspection. Setting them by guessing would violate the project integrity rules.

Once source files are available, `run_matrix.py --execute` audits each slot and runs only combinations whose mapping is verified, whose dataset has at least 2,000 source observations and whose required fields/record keys pass checks. A method/dataset pair may remain not evaluable if the assay, outcome or features do not match. Such a slot must be reported as not applicable rather than forced into a proxy experiment and called a paper reproduction.
