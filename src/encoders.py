# Owner: M3 – Primesh Marasingha
"""
Feature encoding pipeline for the DataCo Late-Delivery REGRESSION task.

Public API
----------
build_encoder(scale_numeric, high_card_strategy)  → ColumnTransformer
build_feature_pipeline(...)                        → Pipeline (M2 feats → encoder)
select_features(X_enc, y, feature_names, ...)      → (importance_df, selected, corr_pairs)

Pipeline layout (inside build_feature_pipeline)
------------------------------------------------
Step 1 – _FeatureAdder
    Runs M2's DateFeatures, OrderFeatures, GeoFeatures on the full DataFrame
    and concatenates their outputs with the original columns.
    Any transformer that raises is skipped with a warning; its columns are
    filled with NaN so the downstream imputer handles them cleanly.

Step 2 – ColumnTransformer  (build_encoder)
    ┌──────────────┬──────────────────────────────┬──────────────────────────┐
    │ ohe          │ CATEGORICAL_LOW (6 cols)      │ OneHotEncoder            │
    │ high_card    │ CATEGORICAL_HIGH (6 cols)     │ TargetEncoder continuous │
    │ num          │ NUMERIC (11 + 9 engineered)   │ Imputer [+ StandardScaler│
    └──────────────┴──────────────────────────────┴──────────────────────────┘
    remainder='drop' silently discards Order Id, order date, Customer Country, etc.

TargetEncoder notes
-------------------
  sklearn >= 1.3, target_type='continuous'.
  During fit_transform the encoder uses internal k-fold cross-fitting to prevent
  target leakage (categories in the training portion never see their own y).
  sklearn's Pipeline passes y through to ColumnTransformer which passes it to
  TargetEncoder via metadata routing — no manual wiring needed.
"""
from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import CATEGORICAL_HIGH, CATEGORICAL_LOW, NUMERIC


# ---------------------------------------------------------------------------
# _FeatureAdder — wraps M2's transformers
# ---------------------------------------------------------------------------

class _FeatureAdder(BaseEstimator, TransformerMixin):
    """
    Applies a list of (name, transformer) pairs to the full DataFrame,
    appends their outputs as new columns, and returns the enriched DataFrame.

    If a transformer fails at fit or transform time it is skipped; its output
    columns are filled with NaN so SimpleImputer can handle them later.
    """

    def __init__(self, named_transformers: list[tuple[str, TransformerMixin]]):
        self.named_transformers = named_transformers

    def fit(self, X: pd.DataFrame, y=None):
        for name, t in self.named_transformers:
            try:
                t.fit(X, y)
            except Exception as exc:
                warnings.warn(f"_FeatureAdder: skipping fit of '{name}': {exc}")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        parts = [X]
        for name, t in self.named_transformers:
            try:
                out = t.transform(X)
                if not isinstance(out, pd.DataFrame):
                    out = pd.DataFrame(
                        out,
                        index=X.index,
                        columns=t.get_feature_names_out(),
                    )
                parts.append(out)
            except Exception as exc:
                warnings.warn(f"_FeatureAdder: skipping transform of '{name}': {exc}")
                # fill with NaN so SimpleImputer recovers
                try:
                    cols = t.get_feature_names_out()
                except Exception:
                    cols = []
                if cols:
                    fallback = pd.DataFrame(
                        np.full((len(X), len(cols)), np.nan),
                        index=X.index,
                        columns=cols,
                    )
                    parts.append(fallback)
        return pd.concat(parts, axis=1)

    def get_feature_names_out(self, input_features=None):
        names = list(input_features) if input_features is not None else []
        for _, t in self.named_transformers:
            try:
                names.extend(t.get_feature_names_out())
            except Exception:
                pass
        return np.array(names)


def _load_m2_transformers() -> list[tuple[str, TransformerMixin]]:
    """Import M2's sklearn transformers; return empty list if unavailable."""
    transformers: list[tuple[str, TransformerMixin]] = []
    try:
        from src.features import DateFeatures, GeoFeatures, OrderFeatures
        transformers = [
            ("date",  DateFeatures()),
            ("order", OrderFeatures()),
            ("geo",   GeoFeatures()),
        ]
    except ImportError as exc:
        warnings.warn(f"M2 feature transformers not available: {exc}")
    except Exception as exc:
        warnings.warn(f"Error loading M2 transformers: {exc}")
    return transformers


# ---------------------------------------------------------------------------
# _FrequencyEncoder — fallback when TargetEncoder cannot be used
# ---------------------------------------------------------------------------

class _FrequencyEncoder(BaseEstimator, TransformerMixin):
    """Category → relative training-set frequency. Unseen categories → 0.0."""

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
# build_encoder
# ---------------------------------------------------------------------------

def build_encoder(
    scale_numeric: bool = False,
    high_card_strategy: str = "target",
) -> ColumnTransformer:
    """
    Build an *unfitted* ColumnTransformer for the regression task.

    Parameters
    ----------
    scale_numeric : bool
        If True, add StandardScaler after SimpleImputer for NUMERIC columns.
        Default False (tree-based models don't need scaling).
    high_card_strategy : {"target", "frequency"}
        "target"    — sklearn.preprocessing.TargetEncoder, continuous mode.
                      Requires sklearn ≥ 1.3; uses internal cross-fitting so
                      training categories never see their own y.
        "frequency" — _FrequencyEncoder: no y needed, any sklearn version.

    Returns
    -------
    ColumnTransformer (unfitted)
    """
    # --- Low-cardinality: OneHotEncoder ---
    ohe = OneHotEncoder(
        handle_unknown="ignore",
        min_frequency=50,       # bin rare categories into 'infrequent_sklearn'
        sparse_output=False,
    )

    # --- High-cardinality ---
    if high_card_strategy == "target":
        from sklearn.preprocessing import TargetEncoder  # sklearn >= 1.3
        high_enc = TargetEncoder(
            target_type="continuous",
            smooth="auto",
            cv=5,
        )
    elif high_card_strategy == "frequency":
        high_enc = _FrequencyEncoder()
    else:
        raise ValueError(
            f"Unknown high_card_strategy {high_card_strategy!r}. "
            "Choose 'target' or 'frequency'."
        )

    # --- Numeric: impute missing, optionally scale ---
    num_steps: list = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    num_pipe = Pipeline(num_steps)

    return ColumnTransformer(
        transformers=[
            ("ohe",       ohe,      CATEGORICAL_LOW),
            ("high_card", high_enc, CATEGORICAL_HIGH),
            ("num",       num_pipe, NUMERIC),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


# ---------------------------------------------------------------------------
# build_feature_pipeline
# ---------------------------------------------------------------------------

def build_feature_pipeline(
    scale_numeric: bool = False,
    high_card_strategy: str = "target",
) -> Pipeline:
    """
    Full preprocessing pipeline:
        _FeatureAdder (M2 transformers) → ColumnTransformer (encoder)

    This pipeline is inserted as the first steps of the training Pipeline
    in train_xgb.py, before the XGBRegressor.

    Parameters
    ----------
    scale_numeric      : passed to build_encoder
    high_card_strategy : passed to build_encoder

    Returns
    -------
    sklearn.pipeline.Pipeline (unfitted)
    """
    m2_transformers = _load_m2_transformers()
    feature_adder   = _FeatureAdder(m2_transformers)
    encoder         = build_encoder(scale_numeric, high_card_strategy)

    return Pipeline([
        ("features", feature_adder),
        ("encoder",  encoder),
    ])


# ---------------------------------------------------------------------------
# select_features
# ---------------------------------------------------------------------------

def select_features(
    X_enc: np.ndarray,
    y: np.ndarray,
    feature_names: np.ndarray | list[str],
    k: int | None = None,
    threshold: float = 0.001,
    corr_threshold: float = 0.95,
) -> tuple[pd.DataFrame, list[str], list[tuple]]:
    """
    Two-stage feature selection using a RandomForestRegressor probe.

    Parameters
    ----------
    X_enc         : post-transform numpy array (already encoded)
    y             : regression target (Days for shipping real)
    feature_names : column names matching X_enc columns
    k             : if given, keep the top-k features (overrides threshold)
    threshold     : minimum normalised importance to keep a feature
    corr_threshold: Pearson |r| above which one feature in a pair is flagged

    Returns
    -------
    importance_df : pd.DataFrame  all features sorted by importance desc
    selected      : list[str]     feature names passing the filter
    corr_pairs    : list of (feat_a, feat_b, r)  highly correlated pairs
    """
    from sklearn.ensemble import RandomForestRegressor

    feature_names = np.array(feature_names)

    probe = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1,
    )
    probe.fit(X_enc, y)

    imp = probe.feature_importances_
    norm_imp = imp / (imp.sum() + 1e-12)

    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": norm_imp})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    if k is not None:
        selected = importance_df.head(k)["feature"].tolist()
    else:
        selected = importance_df.loc[
            importance_df["importance"] >= threshold, "feature"
        ].tolist()

    # Correlation check among selected features
    idx = [i for i, n in enumerate(feature_names) if n in selected]
    X_sel = pd.DataFrame(X_enc[:, idx], columns=np.array(feature_names)[idx])
    corr = X_sel.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1))
    corr_pairs = [
        (c, r, float(upper.loc[r, c]))
        for c in upper.columns
        for r in upper.index
        if pd.notna(upper.loc[r, c]) and upper.loc[r, c] >= corr_threshold
    ]

    print(
        f"select_features: {len(feature_names)} total → "
        f"{len(selected)} kept (threshold={threshold}) | "
        f"{len(corr_pairs)} high-corr pairs (|r| ≥ {corr_threshold})"
    )
    return importance_df, selected, corr_pairs
