import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uti_research.models import build_estimator


def test_logistic_and_random_forest_paper_families_construct():
    assert build_estimator("dedeene_2024_limited_mlr").__class__.__name__ == "LogisticRegression"
    assert build_estimator("lin_2026_seven_feature_rf").__class__.__name__ == "RandomForestClassifier"


def test_voting_ensemble_constructs_when_optional_boosting_libraries_available():
    pytest.importorskip("xgboost")
    pytest.importorskip("lightgbm")
    assert build_estimator("farashi_2025_voting_ensemble").__class__.__name__ == "VotingClassifier"
