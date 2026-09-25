# Owner: M3 – Primesh Marasingha
"""
XGBoost regression pipeline for predicting 'Days for shipping (real)'.

Usage
-----
    python -m src.train_xgb                                   # 5-fold CV + final fit
    python -m src.train_xgb --tune                            # RandomizedSearchCV
    python -m src.train_xgb --split-path data/processed/local # explicit path
    python -m src.train_xgb --no-cv                           # skip CV, fit once fast

Prerequisites
-------------
    python -m src.data_prep_local     # builds data/processed/local/ parquets

Outputs
-------
    models/xgb_pipeline.pkl           trained full pipeline
    models/final_pipeline.pkl         same (alias for backend/app.py)
    results/experiments.csv           appended metrics row
"""
from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import (
    GroupKFold,
    RandomizedSearchCV,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from src.config import (
    DATA_PROCESSED,
    LEAKAGE_R2_THRESHOLD,
    MODELS_DIR,
    RANDOM_SEED,
    RESULTS_DIR,
    SCHEDULED_DAYS,
    TARGET,
)
from src.encoders import build_feature_pipeline


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Train XGBoost regressor for late-delivery days prediction"
    )
    p.add_argument(
        "--split-path",
        default=str(DATA_PROCESSED / "local"),
        help="Directory containing X_train/X_test/y_train/y_test parquets",
    )
    p.add_argument("--tune",    action="store_true", help="RandomizedSearchCV")
    p.add_argument("--no-cv",   action="store_true", help="Skip cross-validation")
    p.add_argument("--cv-folds", type=int, default=5)
    p.add_argument("--n-iter",   type=int, default=30,
                   help="RandomizedSearchCV iterations (--tune only)")
    p.add_argument(
        "--high-card", choices=["target", "frequency"], default="target",
        dest="high_card",
    )
    p.add_argument("--scale-numeric", action="store_true")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Pipeline factory
# ---------------------------------------------------------------------------

def build_pipeline(
    high_card: str = "target",
    scale_numeric: bool = False,
) -> Pipeline:
    """Preprocessing (M2 feats → encoder) + XGBRegressor in one Pipeline."""
    feature_enc = build_feature_pipeline(
        scale_numeric=scale_numeric,
        high_card_strategy=high_card,
    )
    clf = XGBRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.05,
        objective="reg:squarederror",
        tree_method="hist",
        random_state=RANDOM_SEED,
        verbosity=0,
    )
    return Pipeline([
        ("feature_enc", feature_enc),
        ("clf",         clf),
    ])


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_split(path: str | Path) -> tuple:
    """
    Load train/test parquets from *path*.

    Returns
    -------
    X_train, X_test, y_train, y_test, groups_train
    """
    p = Path(path)
    X_train      = pd.read_parquet(p / "X_train.parquet")
    X_test       = pd.read_parquet(p / "X_test.parquet")
    y_train      = pd.read_parquet(p / "y_train.parquet").squeeze()
    y_test       = pd.read_parquet(p / "y_test.parquet").squeeze()
    groups_train = pd.read_parquet(p / "groups_train.parquet").squeeze()
    return X_train, X_test, y_train, y_test, groups_train


def save_model(pipeline: Pipeline, name: str = "xgb_pipeline") -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for stem in [name, "final_pipeline"]:
        out = MODELS_DIR / f"{stem}.pkl"
        joblib.dump(pipeline, out)
        print(f"  Saved → {out}")


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def regression_metrics(y_true, y_pred) -> dict:
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    return {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


def derived_late_flag(
    y_pred: np.ndarray,
    X_test: pd.DataFrame,
    meta_test_path: Path,
) -> dict | None:
    """
    Compute binary late-flag accuracy using:
      predicted_late  = (y_pred > Days for shipment (scheduled))
      ground_truth    = Late_delivery_risk  (from meta_test.parquet)
    """
    if not meta_test_path.exists():
        warnings.warn(f"meta_test.parquet not found at {meta_test_path} — skipping late-flag eval")
        return None
    if "Days for shipment (scheduled)" not in X_test.columns:
        warnings.warn("'Days for shipment (scheduled)' not in X_test — skipping late-flag eval")
        return None

    from sklearn.metrics import accuracy_score, f1_score, classification_report

    meta        = pd.read_parquet(meta_test_path)
    sched       = X_test["Days for shipment (scheduled)"].values
    pred_late   = (y_pred > sched).astype(int)
    true_late   = meta["Late_delivery_risk"].values

    acc = accuracy_score(true_late, pred_late)
    f1  = f1_score(true_late, pred_late, zero_division=0)

    return {
        "late_flag_accuracy": round(acc, 4),
        "late_flag_f1":       round(f1, 4),
    }


def top_features(pipeline: Pipeline, n: int = 15) -> pd.Series:
    try:
        ct           = pipeline.named_steps["feature_enc"].named_steps["encoder"]
        clf          = pipeline.named_steps["clf"]
        feat_names   = ct.get_feature_names_out()
        importances  = clf.feature_importances_
        return (
            pd.Series(importances, index=feat_names)
            .sort_values(ascending=False)
            .head(n)
        )
    except Exception as exc:
        warnings.warn(f"Could not extract feature importances: {exc}")
        return pd.Series(dtype=float)


def log_to_csv(record: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / "experiments.csv"
    df   = pd.DataFrame([record])
    header = not path.exists() or path.stat().st_size == 0
    df.to_csv(path, mode="a", header=header, index=False)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # ---------------------------------------------------------------- load
    print(f"Loading split from {args.split_path} …")
    X_train, X_test, y_train, y_test, groups_train = load_split(args.split_path)
    print(f"  Train: {len(X_train):,} rows  |  Test: {len(X_test):,} rows")
    print(f"  y_train  mean={y_train.mean():.3f}  std={y_train.std():.3f}")

    pipeline = build_pipeline(args.high_card, args.scale_numeric)
    cv       = GroupKFold(n_splits=args.cv_folds)

    # ---------------------------------------------------------------- CV / tune
    if args.tune:
        param_dist = {
            "clf__n_estimators":     [200, 400, 600, 800],
            "clf__max_depth":        [4, 6, 8],
            "clf__learning_rate":    [0.01, 0.05, 0.1],
            "clf__subsample":        [0.7, 0.8, 0.9],
            "clf__colsample_bytree": [0.7, 0.8, 0.9],
            "clf__min_child_weight": [1, 3, 5],
            "clf__gamma":            [0, 0.05, 0.1, 0.3],
        }
        search = RandomizedSearchCV(
            pipeline,
            param_distributions=param_dist,
            n_iter=args.n_iter,
            cv=cv,
            scoring="neg_mean_absolute_error",
            n_jobs=-1,
            random_state=RANDOM_SEED,
            verbose=2,
            refit=True,
        )
        print(f"\nTuning: {args.n_iter} iterations × {args.cv_folds}-fold GroupKFold …")
        t0 = time.time()
        search.fit(X_train, y_train, groups=groups_train)
        print(f"  Best CV MAE : {-search.best_score_:.4f}  ({time.time()-t0:.1f}s)")
        print(f"  Best params : {search.best_params_}")
        pipeline = search.best_estimator_

    elif not args.no_cv:
        print(f"\nCross-validating ({args.cv_folds}-fold GroupKFold) …")
        t0 = time.time()
        cv_res = cross_validate(
            pipeline, X_train, y_train,
            cv=cv,
            groups=groups_train,
            scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"],
            n_jobs=-1,
        )
        elapsed = time.time() - t0
        for key, label in [
            ("test_neg_mean_absolute_error",      "MAE "),
            ("test_neg_root_mean_squared_error",  "RMSE"),
            ("test_r2",                           "R²  "),
        ]:
            vals = cv_res[key]
            sign = -1 if key.startswith("test_neg") else 1
            print(f"  CV {label}: {sign*vals.mean():.4f} ± {vals.std():.4f}")
        print(f"  Elapsed: {elapsed:.1f}s")

        print("\nFitting on full training set …")
        pipeline.fit(X_train, y_train)

    else:
        print("\nSkipping CV (--no-cv). Fitting on full training set …")
        t0 = time.time()
        pipeline.fit(X_train, y_train)
        print(f"  Fit done in {time.time()-t0:.1f}s")

    # ---------------------------------------------------------------- test metrics
    y_pred = pipeline.predict(X_test)
    metrics = regression_metrics(y_test.values, y_pred)

    print(f"\n{'─'*40}")
    print(f"  Hold-out test metrics")
    print(f"  MAE  : {metrics['MAE']}")
    print(f"  RMSE : {metrics['RMSE']}")
    print(f"  R²   : {metrics['R2']}")

    if metrics["R2"] > LEAKAGE_R2_THRESHOLD:
        print(f"\n  ⚠️  WARNING: R² = {metrics['R2']} > {LEAKAGE_R2_THRESHOLD}. "
              f"This is likely a leakage signal — check feature columns!")

    # ---------------------------------------------------------------- derived late flag
    meta_path  = Path(args.split_path) / "meta_test.parquet"
    late_stats = derived_late_flag(y_pred, X_test, meta_path)
    if late_stats:
        print(f"  Derived late-flag accuracy : {late_stats['late_flag_accuracy']}")
        print(f"  Derived late-flag F1       : {late_stats['late_flag_f1']}")

    # ---------------------------------------------------------------- top features
    print(f"\n  Top 15 features by XGBoost gain:")
    top = top_features(pipeline, 15)
    if not top.empty:
        for feat, imp in top.items():
            print(f"    {imp:.4f}  {feat}")
    print(f"{'─'*40}")

    # ---------------------------------------------------------------- save
    save_model(pipeline)

    # ---------------------------------------------------------------- log
    record = {
        "timestamp":  pd.Timestamp.now().isoformat(timespec="seconds"),
        "model":      "xgboost",
        "task":       "regression",
        "split_path": args.split_path,
        "high_card":  args.high_card,
        "tuned":      args.tune,
        **metrics,
        **(late_stats or {}),
    }
    try:
        log_to_csv(record)
        print(f"\nRun logged to results/experiments.csv")
    except Exception as exc:
        print(f"\nWarning: could not log: {exc}")


if __name__ == "__main__":
    main()
