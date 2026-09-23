# Owner: M3 – Primesh Marasingha
"""
Feature encoding pipeline for the DataCo Late Delivery Predictor.

Public API
----------
build_encoder(high_card_strategy)  → ColumnTransformer  (unfitted)
select_features(X_train, y_train, fitted_transformer, ...)  → list[str]

Design
------
ColumnTransformer layout:
  ┌──────────────┬─────────────────────────────┬────────────────────────────┐
  │  Transformer  │  Columns                    │  Strategy                  │
  ├──────────────┼─────────────────────────────┼────────────────────────────┤
  │  ohe          │  CATEGORICAL_LOW (6 cols)   │  OneHotEncoder             │
  │  high_card    │  CATEGORICAL_HIGH (4 cols)  │  TargetEncoder (sklearn≥1.3│
  │               │                             │  or _FrequencyEncoder)     │
  │  num          │  NUMERIC (11 cols)          │  passthrough               │
  └──────────────┴─────────────────────────────┴────────────────────────────┘

All transformers are fitted inside a Pipeline on training data only, preventing
target leakage through the encoder.

TargetEncoder requirement: sklearn >= 1.3 passes y through ColumnTransformer
to TargetEncoder automatically via metadata routing.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from src.config import CATEGORICAL_HIGH, CATEGORICAL_LOW, NUMERIC


# ---------------------------------------------------------------------------
# Frequency encoder (no y needed — works in all sklearn versions)
# ---------------------------------------------------------------------------

class _FrequencyEncoder(BaseEstimator, TransformerMixin):
    """
    Encode each category as its relative frequency in the training set.
    Unseen categories map to 0.0.
    """

    def fit(self, X, y=None):
        X = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X.copy()
        self._freq: dict = {
            col: X[col].value_counts(normalize=True).to_dict()
            for col in X.columns
        }
        self._feature_names: list[str] = list(X.columns)
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self._feature_names)
        return np.column_stack(
            [X[col].map(self._freq.get(col, {})).fillna(0.0).values
             for col in self._feature_names]
        ).astype(float)

    def get_feature_names_out(self, input_features=None) -> np.ndarray:
        names = input_features if input_features is not None else self._feature_names
        return np.array([f"freq__{f}" for f in names])


# ---------------------------------------------------------------------------
# Public: build_encoder
# ---------------------------------------------------------------------------

def build_encoder(high_card_strategy: str = "target") -> ColumnTransformer:
    """
    Build an *unfitted* ColumnTransformer ready to be placed as the first
    step of a sklearn Pipeline.

    Parameters
    ----------
    high_card_strategy : {"target", "frequency"}
        "target"    — sklearn.preprocessing.TargetEncoder (requires sklearn ≥ 1.3).
                      Maps each high-cardinality category to a smoothed estimate
                      of P(late=1 | category).  Requires sklearn to pass y through
                      ColumnTransformer (done automatically in Pipelines ≥ 1.3).
        "frequency" — _FrequencyEncoder: maps each category to its training-set
                      relative frequency.  Needs no y; safe to use in any sklearn
                      version.

    Returns
    -------
    ColumnTransformer  (unfitted)
    """
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    if high_card_strategy == "target":
        from sklearn.preprocessing import TargetEncoder  # noqa: sklearn ≥ 1.3
        high_enc = TargetEncoder(smooth="auto", target_type="binary")
    elif high_card_strategy == "frequency":
        high_enc = _FrequencyEncoder()
    else:
        raise ValueError(
            f"Unknown high_card_strategy {high_card_strategy!r}. "
            "Choose 'target' or 'frequency'."
        )

    return ColumnTransformer(
        transformers=[
            ("ohe",       ohe,      CATEGORICAL_LOW),
            ("high_card", high_enc, CATEGORICAL_HIGH),
            ("num",       "passthrough", NUMERIC),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


# ---------------------------------------------------------------------------
# Public: select_features
# ---------------------------------------------------------------------------

def select_features(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    fitted_transformer: ColumnTransformer,
    importance_threshold: float = 0.001,
    corr_threshold: float = 0.95,
) -> list[str]:
    """
    Two-stage feature selection using a lightweight XGBoost:

    1. Importance filter — keep features whose normalised gain ≥
       ``importance_threshold`` (default 0.001, i.e. 0.1 %).
    2. Correlation pruning — among surviving features, drop one column
       from every pair with |Pearson r| ≥ ``corr_threshold`` (default 0.95).

    This function is for exploratory use in notebooks.  The main training
    pipeline (train_xgb.py) uses all encoded features; call this manually
    to inspect which features carry most signal.

    Parameters
    ----------
    X_train             : raw (pre-transform) training DataFrame
    y_train             : binary target Series
    fitted_transformer  : already-fitted ColumnTransformer (fit on X_train)
    importance_threshold: minimum normalised feature importance to keep
    corr_threshold      : Pearson |r| above which one feature is pruned

    Returns
    -------
    list[str]  post-transform feature names to retain
    """
    from xgboost import XGBClassifier

    X_enc = fitted_transformer.transform(X_train)
    feature_names = np.array(fitted_transformer.get_feature_names_out())

    probe = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        eval_metric="logloss",
        verbosity=0,
    )
    probe.fit(X_enc, y_train)

    imp = probe.feature_importances_
    norm_imp = imp / (imp.sum() + 1e-12)
    keep_mask = norm_imp >= importance_threshold

    selected_names = list(feature_names[keep_mask])
    X_imp = pd.DataFrame(X_enc[:, keep_mask], columns=selected_names)

    corr = X_imp.corr().abs()
    upper_tri = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1))
    to_drop = {col for col in upper_tri.columns if upper_tri[col].max() >= corr_threshold}

    selected = [f for f in selected_names if f not in to_drop]

    print(
        f"select_features: {len(feature_names)} total → "
        f"{len(selected_names)} after importance filter → "
        f"{len(selected)} after correlation pruning"
    )
    return selected
