"""Clinical classification metrics, validation thresholding and honest uncertainty."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score, brier_score_loss,
    confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, roc_curve,
)


def threshold_at_specificity(y_true, probability, minimum_specificity: float = 0.80) -> float:
    """Choose a validation-only cutoff maximizing sensitivity at specificity >= target."""
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probability, dtype=float)
    candidates = np.r_[0.0, np.unique(p), 1.0]
    feasible = []
    for t in candidates:
        pred = p >= t
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        spec = tn / (tn + fp) if tn + fp else 0.0
        sens = tp / (tp + fn) if tp + fn else 0.0
        if spec >= minimum_specificity:
            feasible.append((sens, spec, float(t)))
    if not feasible:
        return 0.5
    return max(feasible, key=lambda x: (x[0], x[1], -x[2]))[2]


def operating_points(y_true, probability) -> dict[str, float]:
    """Report empirical ROC operating points; these do not select the deployment threshold."""
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probability, dtype=float)
    if len(np.unique(y)) != 2:
        return {}
    fpr, tpr, _ = roc_curve(y, p)
    spec = 1.0 - fpr
    out = {}
    for target in (.80, .90, .95):
        eligible = tpr[spec >= target]
        out[f"sensitivity_at_specificity_ge_{target:.2f}"] = float(np.max(eligible)) if len(eligible) else float("nan")
    for target in (.80, .90, .95):
        eligible = spec[tpr >= target]
        out[f"specificity_at_sensitivity_ge_{target:.2f}"] = float(np.max(eligible)) if len(eligible) else float("nan")
    return out


def metrics(y_true, probability, threshold: float = 0.5) -> dict[str, float | int]:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probability, dtype=float)
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    safe = lambda a, b: float(a / b) if b else float("nan")
    out = {
        "threshold": float(threshold), "tn": int(tn), "fp": int(fp),
        "fn": int(fn), "tp": int(tp),
        "accuracy": float(accuracy_score(y, pred)),
        "sensitivity": safe(tp, tp + fn), "specificity": safe(tn, tn + fp),
        "precision_ppv": safe(tp, tp + fp), "npv": safe(tn, tn + fn),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "false_negative_rate": safe(fn, fn + tp),
        "false_positive_rate": safe(fp, fp + tn),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else float("nan"),
        "pr_auc_average_precision": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else float("nan"),
        "brier_score": float(brier_score_loss(y, p)),
    }
    out.update(operating_points(y, p))
    return out


def bootstrap_ci(y_true, probability, threshold: float, n_boot: int = 2000, seed: int = 271828):
    """Row-bootstrap percentile 95% intervals. Cluster bootstrap is needed if repeated
    records per patient are retained; no patient-level intervals are implied here.
    """
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probability, dtype=float)
    rng = np.random.default_rng(seed)
    names = ["accuracy", "sensitivity", "specificity", "precision_ppv", "npv", "f1", "balanced_accuracy", "false_negative_rate", "false_positive_rate", "roc_auc", "pr_auc_average_precision", "brier_score"]
    vals = {k: [] for k in names}
    for _ in range(n_boot):
        ix = rng.integers(0, len(y), size=len(y))
        if len(np.unique(y[ix])) < 2:
            continue
        m = metrics(y[ix], p[ix], threshold)
        for k in names:
            vals[k].append(m[k])
    return {
        k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] if v else [float("nan"), float("nan")]
        for k, v in vals.items()
    }


def paired_bootstrap_auc_difference(y_true, probability_a, probability_b, n_boot: int = 2000, seed: int = 271828):
    """Paired row bootstrap for AUC(A)-AUC(B) on identical held-out observations."""
    y = np.asarray(y_true, dtype=int)
    a = np.asarray(probability_a, dtype=float)
    b = np.asarray(probability_b, dtype=float)
    if len(y) != len(a) or len(y) != len(b):
        raise ValueError("Paired comparison requires predictions on the same rows")
    observed = float(roc_auc_score(y, a) - roc_auc_score(y, b))
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n_boot):
        ix = rng.integers(0, len(y), size=len(y))
        if len(np.unique(y[ix])) == 2:
            values.append(roc_auc_score(y[ix], a[ix]) - roc_auc_score(y[ix], b[ix]))
    ci = np.percentile(values, [2.5, 97.5]).astype(float).tolist() if values else [float("nan"), float("nan")]
    return {"auc_a_minus_b": observed, "paired_bootstrap_95ci": ci, "n_valid_bootstrap": len(values), "interpretation": "CI excluding zero is evidence of a difference under this paired row-bootstrap; use a cluster bootstrap for repeated patients."}
