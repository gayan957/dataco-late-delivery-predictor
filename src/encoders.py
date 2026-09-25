"""M3 – categorical encoding and the preprocessor builder.

Kept in a .py file so the trained pipeline can be pickled and loaded by the backend.
Scaling is added by M4; this module only encodes and assembles the features.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, TargetEncoder

from src.features import DATE_COL, DateFeatures, GeoFeatures, OrderFeatures

LOW_CARD_MAX = 30          # up to 30 categories -> one-hot; more -> high-cardinality strategy
SEED = 42

# Engineered feature "units" (from M2) and the raw columns each one needs
ENGINEERED = {
    "date_features": [DATE_COL],
    "order_features": ["Order Id", "Sales", "Product Name"],
    "geo_features": ["Customer Country", "Order Country"],
}


class FrequencyEncoder(BaseEstimator, TransformerMixin):
    """Replace each category with its share of TRAINING rows. Unseen categories get 0."""

    def fit(self, X, y=None):
        X = pd.DataFrame(X)
        self.columns_ = list(X.columns)
        self.freqs_ = {c: X[c].value_counts(normalize=True) for c in self.columns_}
        return self

    def transform(self, X):
        X = pd.DataFrame(X, columns=self.columns_)
        return np.column_stack([X[c].map(self.freqs_[c]).fillna(0).to_numpy(float) for c in self.columns_])

    def get_feature_names_out(self, input_features=None):
        return np.array([f"{c}_freq" for c in self.columns_])


def high_card_encoder(strategy):
    """Encoder for columns with more than LOW_CARD_MAX categories."""
    if strategy == "onehot_rare":
        # one column per category that covers >= 1% of rows, everything else -> one 'infrequent' column
        return OneHotEncoder(min_frequency=0.01, handle_unknown="infrequent_if_exist", sparse_output=False)
    if strategy == "frequency":
        return FrequencyEncoder()
    if strategy == "target":
        # mean target per category; fit_transform uses internal cross-fitting (out-of-fold means)
        return TargetEncoder(target_type="continuous", random_state=SEED)
    raise ValueError(f"Unknown strategy: {strategy}")


def split_columns(X, features):
    """Sort the raw feature columns into numeric / low-cardinality / high-cardinality."""
    raw = [f for f in features if f not in ENGINEERED]
    numeric = [c for c in raw if pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in raw if c not in numeric]
    low = [c for c in categorical if X[c].nunique() <= LOW_CARD_MAX]
    high = [c for c in categorical if c not in low]
    return numeric, low, high


def build_preprocessor(X, features, high_card="target"):
    """ColumnTransformer for the chosen features.

    features  : raw column names plus any of 'date_features', 'order_features', 'geo_features'
    high_card : 'drop', 'onehot_rare', 'frequency' or 'target'
    """
    numeric, low, high = split_columns(X, features)
    parts = []
    if numeric:
        parts.append(("num", SimpleImputer(strategy="median"), numeric))            # M4 adds scaling
    if low:
        parts.append(("low_card", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), low))
    if high and high_card != "drop":
        parts.append(("high_card", high_card_encoder(high_card), high))
    if "date_features" in features:
        parts.append(("date", Pipeline([("feats", DateFeatures()),
                                        ("impute", SimpleImputer(strategy="most_frequent"))]), [DATE_COL]))
    if "order_features" in features:
        parts.append(("order", OrderFeatures(), ENGINEERED["order_features"]))
    if "geo_features" in features:
        parts.append(("geo", GeoFeatures(), ENGINEERED["geo_features"]))
    return ColumnTransformer(parts, remainder="drop")
