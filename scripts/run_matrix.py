#!/usr/bin/env python3
"""Audit and optionally execute all 3 paper-family x 2 dataset combinations.

Dry-run (safe default):
  python scripts/run_matrix.py --config configs/experiment_matrix.json

Execute only after every row is READY and target/feature mappings have been verified:
  python scripts/run_matrix.py --config configs/experiment_matrix.json --execute

A blocked combination is recorded as blocked, never silently run with surrogate features.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_frame(path: Path):
    import pandas as pd
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def inspect_task(task, config):
    dataset = config["datasets"][task["dataset"]]
    method = config["methods"][task["method"]]
    source = ROOT / dataset["input"]
    report = {
        "experiment_id": task["id"],
        "dataset": task["dataset"],
        "method": task["method"],
        "reference": method["reference"],
        "source_path": str(source.relative_to(ROOT)),
        "paper_feature_spec": method["paper_feature_spec"],
        "compatibility_note": method["compatibility_note"],
    }
    if not source.is_file():
        return {**report, "status": "BLOCKED_DATA_FILE_MISSING"}
    if not dataset.get("mapping_verified"):
        return {**report, "status": "BLOCKED_DATA_MAPPING_UNVERIFIED"}
    required_mapping = ["target_column", "negative_label", "positive_label"]
    if any(dataset.get(key) is None for key in required_mapping):
        return {**report, "status": "BLOCKED_TARGET_MAPPING_INCOMPLETE"}
    features = method.get("dataset_feature_columns")
    if not isinstance(features, list) or not features:
        return {**report, "status": "BLOCKED_FEATURE_MAPPING_UNVERIFIED"}
    df = read_frame(source)
    if len(df) < int(config.get("minimum_original_valid_rows", 2000)):
        return {**report, "status": "REJECTED_BELOW_2000", "original_rows": int(len(df))}
    if df.duplicated().any():
        return {**report, "status": "BLOCKED_EXACT_DUPLICATES", "original_rows": int(len(df)), "exact_duplicate_rows": int(df.duplicated().sum())}
    all_needed = features + [dataset["target_column"]]
    for key in ["patient_id", "record_id"]:
        if dataset.get(key):
            all_needed.append(dataset[key])
    missing = sorted(set(all_needed) - set(df.columns))
    if missing:
        return {**report, "status": "BLOCKED_COLUMNS_MISSING", "missing_columns": missing, "original_rows": int(len(df))}
    if df[dataset["target_column"]].isna().any():
        return {**report, "status": "BLOCKED_TARGET_MISSING_VALUES", "original_rows": int(len(df))}
    observed = {str(v) for v in pd.unique(df[dataset["target_column"]])}
    expected = {str(dataset["negative_label"]), str(dataset["positive_label"])}
    if observed != expected or len(expected) != 2:
        return {**report, "status": "BLOCKED_TARGET_LABEL_MISMATCH", "observed_labels": sorted(observed), "expected_labels": sorted(expected)}
    record_id = dataset.get("record_id")
    if record_id and df[record_id].dropna().duplicated().any():
        return {**report, "status": "BLOCKED_REPEATED_RECORD_IDS", "repeated_record_id_rows": int(df[record_id].dropna().duplicated(keep=False).sum())}
    return {**report, "status": "READY", "original_rows": int(len(df)), "target_counts": {str(k): int(v) for k, v in df[dataset["target_column"]].value_counts().items()}, "features": features}


def execute_task(task, config, report):
    dataset = config["datasets"][task["dataset"]]
    out = ROOT / "results" / "matrix" / task["id"]
    command = [
        sys.executable, str(ROOT / "scripts" / "run_experiment.py"),
        "--input", str(ROOT / dataset["input"]),
        "--target", str(dataset["target_column"]),
        "--negative-label", str(dataset["negative_label"]),
        "--positive-label", str(dataset["positive_label"]),
        "--features", ",".join(config["methods"][task["method"]]["dataset_feature_columns"]),
        "--method", task["method"], "--dataset-id", task["dataset"],
        "--dataset-version", str(dataset["version"]),
        "--seed", str(config.get("seed", 271828)),
        "--output-dir", str(out), "--approved",
    ]
    for key, option in [("patient_id", "--patient-id"), ("record_id", "--record-id")]:
        if dataset.get(key):
            command.extend([option, dataset[key]])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    report["return_code"] = completed.returncode
    report["stdout"] = completed.stdout[-4000:]
    report["stderr"] = completed.stderr[-4000:]
    report["status"] = "COMPLETED" if completed.returncode == 0 else "FAILED"
    report["results_dir"] = str(out.relative_to(ROOT))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment_matrix.json")
    parser.add_argument("--execute", action="store_true", help="Run READY combinations; otherwise only audit and report statuses")
    parser.add_argument("--output", default="results/experiment_matrix_status.json")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    tasks = config.get("experiments", [])
    if len(tasks) != 6 or len({(x["dataset"], x["method"]) for x in tasks}) != 6:
        raise SystemExit("Matrix config must contain exactly six unique dataset-method combinations")
    reports = []
    for task in tasks:
        result = inspect_task(task, config)
        if args.execute and result["status"] == "READY":
            result = execute_task(task, config, result)
        reports.append(result)
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"matrix_name": config.get("matrix_name"), "execution_requested": args.execute, "experiments": reports}
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
