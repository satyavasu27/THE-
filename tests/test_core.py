import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import pytest
from uti_research.audit import audit_frame
from uti_research.evaluation import metrics, threshold_at_specificity, paired_bootstrap_auc_difference


def test_audit_reports_original_duplicates_and_missing_target():
    frame = pd.DataFrame({"patient": [1, 1, 2], "y": [1, 1, None], "x": [3, 3, 4]})
    result = audit_frame(frame, "y", "patient")
    assert result["original_rows"] == 3
    assert result["exact_duplicate_rows"] == 1
    assert result["missing_target"] == 1
    assert result["unique_nonmissing_patients"] == 2


def test_clinical_metrics_and_validation_threshold():
    y = [0, 0, 1, 1]
    p = [0.1, 0.8, 0.7, 0.9]
    threshold = threshold_at_specificity(y, p, minimum_specificity=0.5)
    m = metrics(y, p, threshold)
    assert m["tn"] + m["fp"] == 2
    assert m["tp"] + m["fn"] == 2
    assert 0 <= m["sensitivity"] <= 1
    assert 0 <= m["specificity"] <= 1
    assert m["roc_auc"] == pytest.approx(0.75)
    assert 0 <= m["brier_score"] <= 1


def test_paired_bootstrap_requires_same_observations_and_is_reproducible():
    y = [0, 0, 1, 1]
    a = [0.1, 0.6, 0.7, 0.9]
    b = [0.2, 0.8, 0.6, 0.7]
    result = paired_bootstrap_auc_difference(y, a, b, n_boot=100, seed=7)
    assert result["auc_a_minus_b"] > 0
    assert result["n_valid_bootstrap"] > 0
    with pytest.raises(ValueError):
        paired_bootstrap_auc_difference(y, a, b[:3])


def test_rejects_missing_target_column():
    with pytest.raises(KeyError):
        audit_frame(pd.DataFrame({"x": [1]}), "missing")
