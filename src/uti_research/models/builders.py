"""Paper-aligned estimator builders; unspecified choices are explicit adaptations."""
from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


def build_estimator(method: str, seed: int = 271828):
    """Build a paper-family model with conservative, documented local defaults.

    These are not asserted to be the authors' exact hyperparameters. In particular,
    the 2025 paper's XGBoost / decision-tree / LightGBM vote requires both optional
    libraries. Missing dependencies fail loudly rather than silently substituting.
    """
    if method == "dedeene_2024_limited_mlr":
        # scikit-learn documented defaults; exact source-paper solver/regularization
        # settings are not asserted. This is an adaptation pending full extraction.
        return LogisticRegression(random_state=seed)
    if method == "farashi_2025_voting_ensemble":
        try:
            from xgboost import XGBClassifier
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise RuntimeError("Voting methodology requires xgboost and lightgbm") from exc
        return VotingClassifier(
            estimators=[
                ("xgb", XGBClassifier(random_state=seed, eval_metric="logloss", n_jobs=1)),
                ("dt", DecisionTreeClassifier(random_state=seed)),
                ("lgbm", LGBMClassifier(random_state=seed, verbosity=-1, n_jobs=1)),
            ],
            # Equal weights follow the source report; soft voting is an explicit
            # implementation choice unless the paper's exact voting semantics are confirmed.
            voting="soft",
            weights=[1, 1, 1],
        )
    if method == "lin_2026_seven_feature_rf":
        # RandomForestClassifier's documented library default is used here because
        # the paper-specific tree count/settings have not yet been independently verified.
        return RandomForestClassifier(class_weight="balanced", random_state=seed, n_jobs=1)
    raise ValueError(f"Unknown methodology profile: {method}")
