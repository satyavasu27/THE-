#!/usr/bin/env python3
"""Count original rows/duplicates/missingness without modifying input data."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uti_research.audit import write_audit

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--input", required=True)
p.add_argument("--target", required=True)
p.add_argument("--patient-id")
p.add_argument("--record-id", help="Verified source key defining one analytic record, if available")
p.add_argument("--output", default="results/tables/dataset_audit.json")
a = p.parse_args()
report = write_audit(a.input, a.target, a.output, a.patient_id, a.record_id)
print(json.dumps(report, indent=2))
if not report["size_gate_passed"]:
    raise SystemExit("STOP: fewer than 2,000 valid unique target rows; reject dataset")
