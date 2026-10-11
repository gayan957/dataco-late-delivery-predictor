"""
tests/test_no_leakage.py
Validates the data pipeline against the two hardest leakage rules:

  1. No leakage column (Days for shipping real, Delivery Status, etc.)
     survives clean().
  2. No Order Id appears in both the train and test partitions.

Both tests skip gracefully when their prerequisites (CSV / parquets) are absent
or when M1's stubs haven't been implemented yet.  Once M1 implements clean()
and make_split() and provides the CSV, these tests must pass before any model
is trained.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import DATA_PROCESSED, LEAKAGE_COLS


# ---------------------------------------------------------------------------
# Test 1 – leakage columns
# ---------------------------------------------------------------------------

def test_clean_removes_leakage_columns():
    """
    After data_prep.clean(), none of the LEAKAGE_COLS should be present.

    Skips if:
    - clean() raises NotImplementedError (M1 stub)
    - The raw CSV is not present in data/raw/
    """
    try:
        from src.data_prep import clean, load_raw
    except ImportError as exc:
        pytest.skip(f"Cannot import data_prep: {exc}")

    try:
        df_raw = load_raw()
    except NotImplementedError:
        pytest.skip("load_raw() not yet implemented (M1 stub)")
    except FileNotFoundError:
        pytest.skip(
            "Raw CSV not found in data/raw/ — "
            "add DataCoSupplyChainDataset.csv to run this test"
        )

    try:
        df_clean = clean(df_raw)
    except NotImplementedError:
        pytest.skip("clean() not yet implemented (M1 stub)")

    for col in LEAKAGE_COLS:
        assert col not in df_clean.columns, (
            f"Leakage column '{col}' survived clean(). "
            "Remove it in data_prep.clean() — it is only available post-delivery."
        )


# ---------------------------------------------------------------------------
# Test 2 – order id overlap
# ---------------------------------------------------------------------------

def test_no_order_id_overlap_between_train_and_test():
    """
    No Order Id should appear in both the train and test partitions.
    A plain random split would allow the same order's items to land on
    both sides, letting the model memorise order-level patterns.

    Skips if the split parquets haven't been generated yet (run `make split`).
    """
    x_train_path = DATA_PROCESSED / "X_train.parquet"
    x_test_path  = DATA_PROCESSED / "X_test.parquet"

    if not x_train_path.exists() or not x_test_path.exists():
        pytest.skip(
            "Split parquets not found in data/processed/ — "
            "run `make split` first (requires M1's clean() to be implemented)"
        )

    X_train = pd.read_parquet(x_train_path)
    X_test  = pd.read_parquet(x_test_path)

    if "Order Id" not in X_train.columns or "Order Id" not in X_test.columns:
        pytest.skip(
            "'Order Id' column not present in split files — "
            "ensure data_prep.make_split() preserves it in X_train/X_test"
        )

    train_ids = set(X_train["Order Id"].unique())
    test_ids  = set(X_test["Order Id"].unique())
    overlap   = train_ids & test_ids

    assert len(overlap) == 0, (
        f"{len(overlap):,} Order Ids appear in BOTH train and test partitions.\n"
        "Use GroupShuffleSplit(groups=df['Order Id']) in data_prep.make_split() "
        "to keep all items of the same order in the same split."
    )
