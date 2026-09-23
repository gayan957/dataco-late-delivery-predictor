# Owner: M1
"""
Load, clean, and split the DataCo Supply Chain dataset.

Pipeline:
    load_raw() → clean() → make_split()

Saved artefacts (data/processed/):
    X_train.parquet, X_test.parquet
    y_train.parquet, y_test.parquet
    groups_train.parquet  ← Order Id series for StratifiedGroupKFold
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit

from src.config import (
    DATA_RAW,
    DATA_PROCESSED,
    LEAKAGE_COLS,
    DROP_COLS,
    CANCELLED_STATUSES,
    TARGET,
    RANDOM_SEED,
)


def load_raw() -> pd.DataFrame:
    """
    Load the raw DataCo CSV (LATIN-1 encoded, 180,519 rows × 53 cols).

    Returns
    -------
    pd.DataFrame
    """
    # TODO M1: read DATA_RAW with encoding="latin-1"
    raise NotImplementedError(
        "TODO M1 — load DATA_RAW with pd.read_csv(..., encoding='latin-1')"
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply data-quality rules and remove leakage.

    Steps (in order):
    1. Drop rows where Order Status ∈ CANCELLED_STATUSES  (~7,754 rows).
    2. Drop all columns in LEAKAGE_COLS.
    3. Drop all columns in DROP_COLS.

    Parameters
    ----------
    df : pd.DataFrame  raw output of load_raw()

    Returns
    -------
    pd.DataFrame  ~172,765 rows, leakage-free
    """
    # TODO M1:
    #   df = df[~df["Order Status"].isin(CANCELLED_STATUSES)].copy()
    #   df = df.drop(columns=LEAKAGE_COLS, errors="ignore")
    #   df = df.drop(columns=DROP_COLS, errors="ignore")
    raise NotImplementedError(
        "TODO M1 — filter CANCELLED_STATUSES, drop LEAKAGE_COLS and DROP_COLS"
    )


def make_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Grouped train/test split: all items sharing an Order Id land in the
    same partition (prevents target leakage through order-level features).

    Uses GroupShuffleSplit with groups=df["Order Id"].

    Saves to DATA_PROCESSED:
        X_train.parquet, X_test.parquet
        y_train.parquet, y_test.parquet
        groups_train.parquet

    Parameters
    ----------
    df        : cleaned DataFrame (output of clean())
    test_size : fraction reserved for the hold-out test set (default 0.2)

    Returns
    -------
    X_train, X_test : pd.DataFrame  (features only, TARGET column excluded)
    y_train, y_test : pd.Series     (TARGET column)
    groups_train    : pd.Series     (Order Id for StratifiedGroupKFold in CV)
    """
    # TODO M1:
    #   X = df.drop(columns=[TARGET])
    #   y = df[TARGET]
    #   groups = df["Order Id"]
    #   gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=RANDOM_SEED)
    #   train_idx, test_idx = next(gss.split(X, y, groups=groups))
    #   X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    #   y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    #   groups_train = groups.iloc[train_idx]
    #   DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    #   X_train.to_parquet(DATA_PROCESSED / "X_train.parquet")
    #   ... (save all five files)
    #   return X_train, X_test, y_train, y_test, groups_train
    raise NotImplementedError(
        "TODO M1 — GroupShuffleSplit on 'Order Id', save parquets to DATA_PROCESSED"
    )


if __name__ == "__main__":
    print("Loading raw data...")
    df_raw = load_raw()
    print(f"  Loaded {len(df_raw):,} rows")
    print("Cleaning...")
    df_clean = clean(df_raw)
    print(f"  After clean: {len(df_clean):,} rows")
    print("Splitting...")
    X_tr, X_te, y_tr, y_te, groups_tr = make_split(df_clean)
    print(f"  Train: {len(X_tr):,}  Test: {len(X_te):,}")
    print("Done. Parquets saved to data/processed/")
