# Owner: M3 – Primesh Marasingha
"""
Local regression split — M3 bridge until M1 delivers the corrected parquet split.

Applies the regression leakage rules, does GroupShuffleSplit on Order Id,
and writes parquets to data/processed/local/.

Usage
-----
    python -m src.data_prep_local          # creates data/processed/local/
    python -m src.data_prep_local --dry-run

Output files (data/processed/local/)
--------------------------------------
    X_train.parquet     feature matrix, includes Order Id and order date
    X_test.parquet
    y_train.parquet     Days for shipping (real)
    y_test.parquet
    groups_train.parquet  Order Id series for GroupKFold in train_xgb.py
    meta_test.parquet   Late_delivery_risk  (for derived late-flag accuracy)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from src.config import (
    CANCELLED_STATUSES,
    DATA_RAW,
    DATA_PROCESSED,
    DROP_COLS,
    LEAKAGE_COLS,
    RANDOM_SEED,
    TARGET,
)

LOCAL_DIR = DATA_PROCESSED / "local"


def _build(test_size: float = 0.2, dry_run: bool = False):
    print(f"Loading {DATA_RAW} …")
    df = pd.read_csv(DATA_RAW, encoding="latin-1")
    print(f"  Raw: {len(df):,} rows × {df.shape[1]} cols")

    # 1. Filter cancelled / fraud orders
    before = len(df)
    df = df[~df["Order Status"].isin(CANCELLED_STATUSES)].copy()
    print(f"  After removing {before - len(df):,} cancelled/fraud rows: {len(df):,}")

    # 2. Save Late_delivery_risk and scheduled days BEFORE dropping leakage,
    #    so we can compute derived late-flag accuracy at evaluation time.
    meta_cols = ["Late_delivery_risk", "Days for shipment (scheduled)"]
    meta_df   = df[meta_cols].copy().reset_index(drop=True)

    # 3. Drop leakage columns (includes Late_delivery_risk)
    df = df.drop(columns=LEAKAGE_COLS, errors="ignore")

    # 4. Drop PII / duplicate / constant columns
    df = df.drop(columns=DROP_COLS, errors="ignore")

    # Sanity: target must still be present
    assert TARGET in df.columns, f"Target column '{TARGET}' missing after drops!"

    # 5. Separate target and features
    y      = df[TARGET].copy()
    X      = df.drop(columns=[TARGET])
    groups = X["Order Id"]  # kept in X for OrderFeatures groupby; dropped by CT

    print(f"  Feature columns ({len(X.columns)}): {sorted(X.columns.tolist())}")
    print(f"  Target '{TARGET}': mean={y.mean():.2f}, std={y.std():.2f}, "
          f"min={y.min()}, max={y.max()}")

    if dry_run:
        print("Dry-run mode — no files written.")
        return

    # 6. Grouped split (GroupShuffleSplit so all items of one order stay together)
    gss = GroupShuffleSplit(
        n_splits=1, test_size=test_size, random_state=RANDOM_SEED
    )
    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train, X_test       = X.iloc[train_idx].reset_index(drop=True), \
                            X.iloc[test_idx].reset_index(drop=True)
    y_train, y_test       = y.iloc[train_idx].reset_index(drop=True), \
                            y.iloc[test_idx].reset_index(drop=True)
    groups_train          = groups.iloc[train_idx].reset_index(drop=True)
    meta_test             = meta_df.iloc[test_idx].reset_index(drop=True)

    n_orders_train = groups_train.nunique()
    n_orders_test  = X_test["Order Id"].nunique()
    overlap        = set(groups_train.unique()) & set(X_test["Order Id"].unique())

    print(f"\nSplit summary")
    print(f"  Train: {len(X_train):,} rows | {n_orders_train:,} unique orders | "
          f"mean target={y_train.mean():.3f}")
    print(f"  Test:  {len(X_test):,} rows  | {n_orders_test:,} unique orders  | "
          f"mean target={y_test.mean():.3f}")
    print(f"  Order Id overlap (must be 0): {len(overlap)}")
    assert len(overlap) == 0, "Group leakage detected — check GroupShuffleSplit!"

    # 7. Save
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)

    X_train.to_parquet(LOCAL_DIR / "X_train.parquet",      index=False)
    X_test.to_parquet(LOCAL_DIR / "X_test.parquet",        index=False)
    y_train.to_frame(name=TARGET).to_parquet(LOCAL_DIR / "y_train.parquet", index=False)
    y_test.to_frame(name=TARGET).to_parquet(LOCAL_DIR / "y_test.parquet",   index=False)
    groups_train.to_frame(name="Order Id").to_parquet(
        LOCAL_DIR / "groups_train.parquet", index=False
    )
    meta_test.to_parquet(LOCAL_DIR / "meta_test.parquet", index=False)

    # 8. Write a small summary JSON
    summary = {
        "task":          "regression",
        "target":        TARGET,
        "split_dir":     str(LOCAL_DIR),
        "train_rows":    int(len(X_train)),
        "test_rows":     int(len(X_test)),
        "train_orders":  int(n_orders_train),
        "test_orders":   int(n_orders_test),
        "feature_cols":  sorted(X_train.columns.tolist()),
        "y_train_mean":  round(float(y_train.mean()), 4),
        "y_test_mean":   round(float(y_test.mean()),  4),
    }
    with open(LOCAL_DIR / "split_meta_local.json", "w") as fh:
        json.dump(summary, fh, indent=2)

    print(f"\nSaved to {LOCAL_DIR}/")
    for f in sorted(LOCAL_DIR.iterdir()):
        print(f"  {f.name}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Build local regression split")
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    _build(test_size=args.test_size, dry_run=args.dry_run)
