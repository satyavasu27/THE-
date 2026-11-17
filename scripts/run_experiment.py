#!/usr/bin/env python3
"""Run one paper-family model on a real CSV/Parquet dataset after audit/compatibility approval.

Example (only after the data gate is passed):
  python scripts/run_experiment.py --input data/raw/cohort.csv --target culture_positive \\
    --negative-label 0 --positive-label 1 --features age,sex,nitrite,wbc,bacteria \\
    --method lin_2026_seven_feature_rf --dataset-id source_name --dataset-version v1 \\
    --output-dir results/source_name/rf

This does not assert faithful reproduction when source features, labels or original
hyperparameters differ. Threshold is selected on validation only; test is untouched
until final evaluation.
"""
from __future__ import annotations
import argparse, json, sys, time, uuid, platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay)
from sklearn.calibration import calibration_curve
from sklearn.model_selection import (StratifiedGroupKFold, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uti_research.evaluation import bootstrap_ci, metrics, threshold_at_specificity
from uti_research.models import build_estimator
from uti_research.audit import sha256


def split_indices(X, y, groups, seed):
    if groups is not None:
        # Approximately 60/20/20, patient-grouped and outcome-stratified when feasible.
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
        folds = list(cv.split(X, y, groups=groups))
        test = folds[0][1]
        val = folds[1][1]
        train = np.concatenate([folds[i][1] for i in (2, 3, 4)])
        return train, val, test, "StratifiedGroupKFold(5); folds 0/1 held out"
    idx = np.arange(len(y))
    trainval, test = train_test_split(idx, test_size=.20, random_state=seed, stratify=y)
    train, val = train_test_split(trainval, test_size=.25, random_state=seed, stratify=y[trainval])
    return train, val, test, "stratified 60/20/20 row split"


def make_pipeline(X, estimator, scale_numeric=False):
    numeric = X.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    num_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scale", StandardScaler()))
    cat_pipe = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                         ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    prep = ColumnTransformer([
        ("num", Pipeline(num_steps), numeric),
        ("cat", cat_pipe, categorical),
    ], remainder="drop")
    return Pipeline([("preprocess", prep), ("model", estimator)])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--negative-label", required=True, help="Exact source label mapped to 0")
    ap.add_argument("--positive-label", required=True, help="Exact source label mapped to 1")
    ap.add_argument("--features", required=True, help="Comma-separated exact input columns")
    ap.add_argument("--method", required=True, choices=[
        "dedeene_2024_limited_mlr", "farashi_2025_voting_ensemble", "lin_2026_seven_feature_rf"])
    ap.add_argument("--dataset-id", required=True)
    ap.add_argument("--dataset-version", required=True, help="Source version/release identifier")
    ap.add_argument("--patient-id")
    ap.add_argument("--record-id", help="Source key defining one observation; repeated IDs must be resolved before run")
    ap.add_argument("--seed", type=int, default=271828)
    ap.add_argument("--minimum-specificity", type=float, default=.80)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--approved", action="store_true", help="Acknowledge data/label/size audit passed")
    args = ap.parse_args()
    if not args.approved:
        ap.error("Refusing to run: complete local 2,000-row, duplicate, target and compatibility audit first; pass --approved only after review.")
    path = Path(args.input)
    df = pd.read_parquet(path) if path.suffix.lower() in {".parquet", ".pq"} else pd.read_csv(path, low_memory=False)
    if len(df) < 2000:
        raise SystemExit(f"STOP: only {len(df)} source rows; minimum is 2,000 before modeling")
    if df.duplicated().any():
        raise SystemExit(f"STOP: {int(df.duplicated().sum())} exact duplicate rows remain; resolve/document before modeling")
    if args.record_id and args.record_id in df and df[args.record_id].dropna().duplicated().any():
        raise SystemExit("STOP: repeated record IDs remain; resolve the analytic unit before modeling")
    features = [x.strip() for x in args.features.split(",") if x.strip()]
    if args.target in features or args.patient_id in features or args.record_id in features:
        raise SystemExit("Target and identifier fields cannot be model input features")
    required = features + [args.target] + ([args.patient_id] if args.patient_id else []) + ([args.record_id] if args.record_id else [])
    missing_cols = sorted(set(required) - set(df.columns))
    if missing_cols:
        raise SystemExit(f"Required columns missing: {missing_cols}")
    # Retain all original observations; only target-missing rows cannot be supervised.
    # Do not de-duplicate here. Apply the audit's pre-registered unit-of-analysis rules first.
    if df[args.target].isna().any():
        raise SystemExit("Target contains missing values; resolve and document using the dataset protocol before training.")
    labels = {str(v) for v in pd.unique(df[args.target].dropna())}
    expected = {str(args.negative_label), str(args.positive_label)}
    if labels != expected or len(labels) != 2:
        raise SystemExit(f"Observed labels {sorted(labels)} do not exactly match the explicitly declared negative/positive labels {sorted(expected)}")
    label_text = df[args.target].astype("string")
    y = (label_text == str(args.positive_label)).astype(int).to_numpy()
    X = df[features].copy()
    groups = None
    if args.patient_id:
        # A missing patient key is assigned a unique row group; it cannot connect unknown
        # repeated records, so this limitation is explicitly logged.
        groups = df[args.patient_id].astype("string").fillna(pd.Series([f"MISSING_ROW_{i}" for i in range(len(df))], index=df.index)).to_numpy()
    train, val, test, split_name = split_indices(X, y, groups, args.seed)
    estimator = build_estimator(args.method, args.seed)
    pipe = make_pipeline(X.iloc[train], estimator, scale_numeric=args.method.endswith("mlr"))
    start = time.perf_counter()
    pipe.fit(X.iloc[train], y[train])
    fit_seconds = time.perf_counter() - start
    classes = list(pipe.named_steps["model"].classes_)
    positive_col = classes.index(1)
    p_train = pipe.predict_proba(X.iloc[train])[:, positive_col]
    p_val = pipe.predict_proba(X.iloc[val])[:, positive_col]
    p_test = pipe.predict_proba(X.iloc[test])[:, positive_col]
    threshold = threshold_at_specificity(y[val], p_val, args.minimum_specificity)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    package_versions = {}
    for package in ["numpy", "pandas", "scikit-learn", "matplotlib", "xgboost", "lightgbm"]:
        try:
            package_versions[package] = version(package)
        except PackageNotFoundError:
            package_versions[package] = None
    timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = str(uuid.uuid4())
    summary = {
        "experiment_id": run_id, "timestamp_utc": timestamp_utc,
        "dataset_id": args.dataset_id, "dataset_version": args.dataset_version,
        "input": str(path), "input_sha256": sha256(path),
        "software_versions": {"python": platform.python_version(), **package_versions},
        "method": args.method,
        "target": args.target, "features": features, "seed": args.seed,
        "split": split_name, "n_total": len(df), "n_train": len(train),
        "n_validation": len(val), "n_test": len(test), "fit_seconds": fit_seconds,
        "threshold_source": "validation only",
        "minimum_validation_specificity": args.minimum_specificity,
        "threshold": threshold,
        "validation_specificity_constraint_met": metrics(y[val], p_val, threshold)["specificity"] >= args.minimum_specificity,
        "train": metrics(y[train], p_train, threshold),
        "validation": metrics(y[val], p_val, threshold),
        "test": metrics(y[test], p_test, threshold),
        "test_bootstrap_95ci_row_level": bootstrap_ci(y[test], p_test, threshold, seed=args.seed),
        "caveat": "No inference to clinical UTI; intervals are row bootstrap, not patient-cluster bootstrap.",
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n")
    pd.DataFrame([{"split": s, **metrics(y[ix], pp, threshold)} for s, ix, pp in
                   [("train", train, p_train), ("validation", val, p_val), ("test", test, p_test)]]).to_csv(out / "metrics.csv", index=False)
    # Final test visualizations use the preselected validation threshold.
    fig, ax = plt.subplots(figsize=(5, 4)); RocCurveDisplay.from_predictions(y[test], p_test, ax=ax); fig.tight_layout(); fig.savefig(out / "roc.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 4)); PrecisionRecallDisplay.from_predictions(y[test], p_test, ax=ax); fig.tight_layout(); fig.savefig(out / "precision_recall.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(4, 4)); ConfusionMatrixDisplay.from_predictions(y[test], p_test >= threshold, labels=[0,1], display_labels=["negative", "positive"], ax=ax, colorbar=False); fig.tight_layout(); fig.savefig(out / "confusion_matrix.png", dpi=160); plt.close(fig)
    frac_pos, mean_pred = calibration_curve(y[test], p_test, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(5, 4)); ax.plot(mean_pred, frac_pos, marker="o"); ax.plot([0,1],[0,1], linestyle="--", color="gray"); ax.set(xlabel="Mean predicted probability", ylabel="Observed positive fraction", title="Calibration (test set)"); fig.tight_layout(); fig.savefig(out / "calibration.png", dpi=160); plt.close(fig)
    # Importance is calculated on validation data only. Correlated variables can split importance.
    perm = permutation_importance(pipe, X.iloc[val], y[val], scoring="roc_auc", n_repeats=10, random_state=args.seed, n_jobs=1)
    imp = pd.DataFrame({"feature": features, "importance_mean": perm.importances_mean, "importance_sd": perm.importances_std}).sort_values("importance_mean", ascending=False)
    imp.to_csv(out / "validation_permutation_importance.csv", index=False)
    top = imp.head(20).sort_values("importance_mean")
    fig, ax = plt.subplots(figsize=(7, max(4, len(top) * .28)))
    ax.barh(top["feature"], top["importance_mean"], xerr=top["importance_sd"])
    ax.set(xlabel="Validation AUROC decrease after permutation", title="Permutation importance (validation only)")
    fig.tight_layout(); fig.savefig(out / "feature_importance.png", dpi=160); plt.close(fig)
    (out / "run.json").write_text(json.dumps({**summary, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2, allow_nan=True) + "\n")
    print(json.dumps(summary, indent=2, allow_nan=True))

if __name__ == "__main__": main()
