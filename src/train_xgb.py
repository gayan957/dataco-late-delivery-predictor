# Owner: M3 – Primesh Marasingha
"""
XGBoost training pipeline for DataCo Late Delivery prediction.

Usage
-----
    python -m src.train_xgb                         # 5-fold CV then final fit
    python -m src.train_xgb --tune                  # RandomizedSearchCV
    python -m src.train_xgb --tune --n-iter 50      # more search iterations
    python -m src.train_xgb --high-card frequency   # use frequency encoding

Prerequisites
-------------
    Run `make split` first (M1's data_prep.make_split()) to produce
    data/processed/*.parquet.

Outputs
-------
    models/xgb_pipeline.pkl       — trained pipeline
    models/final_pipeline.pkl     — same (loaded by backend/app.py)
    results/experiments.csv       — appended metrics row (requires M4)
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedGroupKFold,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.config import DATA_PROCESSED, MODELS_DIR, RANDOM_SEED, RESULTS_DIR
from src.encoders import build_encoder


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Train XGBoost pipeline for late delivery prediction"
    )
    p.add_argument(
        "--tune", action="store_true",
        help="Run RandomizedSearchCV instead of a single fit",
    )
    p.add_argument("--cv-folds", type=int, default=5, metavar="N")
    p.add_argument("--n-iter", type=int, default=30, metavar="N",
                   help="RandomizedSearchCV iterations (only with --tune)")
    p.add_argument(
        "--high-card", choices=["target", "frequency"], default="target",
        dest="high_card",
        help="Encoding strategy for high-cardinality categorical columns",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Pipeline factory
# ---------------------------------------------------------------------------

def build_pipeline(high_card_strategy: str = "target") -> Pipeline:
    """
    Compose encoder + XGBClassifier into a single sklearn Pipeline.

    The encoder (ColumnTransformer) is always the first step so that
    target encoding is re-fitted on each CV fold's training data,
    preventing any look-ahead leakage.
    """
    encoder = build_encoder(high_card_strategy)
    clf = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        scale_pos_weight=1.0,   # adjust if class imbalance is severe
        random_state=RANDOM_SEED,
        eval_metric="logloss",
        verbosity=0,
        tree_method="hist",     # fast histogram-based method
    )
    return Pipeline([("encoder", encoder), ("clf", clf)])


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_split() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Load train/test parquets written by data_prep.make_split().

    Returns
    -------
    X_train, X_test, y_train, y_test, groups_train
    """
    X_train = pd.read_parquet(DATA_PROCESSED / "X_train.parquet")
    X_test  = pd.read_parquet(DATA_PROCESSED / "X_test.parquet")
    y_train = pd.read_parquet(DATA_PROCESSED / "y_train.parquet").squeeze()
    y_test  = pd.read_parquet(DATA_PROCESSED / "y_test.parquet").squeeze()
    groups_train = pd.read_parquet(DATA_PROCESSED / "groups_train.parquet").squeeze()
    return X_train, X_test, y_train, y_test, groups_train


def save_model(pipeline: Pipeline, name: str = "xgb_pipeline") -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    path = MODELS_DIR / f"{name}.pkl"
    joblib.dump(pipeline, path)
    print(f"  Saved → {path}")

    # Always keep final_pipeline.pkl in sync for the backend
    final = MODELS_DIR / "final_pipeline.pkl"
    joblib.dump(pipeline, final)
    print(f"  Saved → {final}")


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    return {
        "model":     "xgboost",
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_proba), 4),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading split from data/processed/…")
    X_train, X_test, y_train, y_test, groups_train = load_split()
    print(f"  Train: {len(X_train):,}  Test: {len(X_test):,}  "
          f"Positive rate: {y_train.mean():.1%}")

    pipeline = build_pipeline(args.high_card)
    cv = StratifiedGroupKFold(
        n_splits=args.cv_folds, shuffle=True, random_state=RANDOM_SEED
    )

    # ----------------------------------------------------------------
    # Cross-validation / tuning
    # ----------------------------------------------------------------
    if args.tune:
        param_dist = {
            "clf__n_estimators":     [200, 400, 600],
            "clf__max_depth":        [4, 6, 8],
            "clf__learning_rate":    [0.01, 0.05, 0.1],
            "clf__subsample":        [0.7, 0.8, 0.9],
            "clf__colsample_bytree": [0.7, 0.8, 0.9],
            "clf__min_child_weight": [1, 3, 5],
            "clf__gamma":            [0, 0.1, 0.3],
        }
        search = RandomizedSearchCV(
            pipeline,
            param_distributions=param_dist,
            n_iter=args.n_iter,
            cv=cv,
            scoring="roc_auc",
            n_jobs=-1,
            random_state=RANDOM_SEED,
            verbose=2,
            refit=True,
        )
        print(f"\nTuning: {args.n_iter} iterations × {args.cv_folds}-fold "
              f"StratifiedGroupKFold CV…")
        t0 = time.time()
        search.fit(X_train, y_train, groups=groups_train)
        elapsed = time.time() - t0
        print(f"  Best CV ROC-AUC : {search.best_score_:.4f}  ({elapsed:.1f}s)")
        print(f"  Best params     : {search.best_params_}")
        pipeline = search.best_estimator_

    else:
        print(f"\nCross-validating ({args.cv_folds}-fold StratifiedGroupKFold)…")
        t0 = time.time()
        cv_res = cross_validate(
            pipeline, X_train, y_train,
            cv=cv,
            groups=groups_train,
            scoring=["roc_auc", "f1", "accuracy"],
            n_jobs=-1,
            return_train_score=False,
        )
        elapsed = time.time() - t0
        for metric in ("roc_auc", "f1", "accuracy"):
            scores = cv_res[f"test_{metric}"]
            print(f"  CV {metric:8s}: {scores.mean():.4f} ± {scores.std():.4f}")
        print(f"  Elapsed: {elapsed:.1f}s")

        print("\nFitting final pipeline on full training set…")
        pipeline.fit(X_train, y_train)

    # ----------------------------------------------------------------
    # Hold-out test evaluation
    # ----------------------------------------------------------------
    test_metrics = evaluate(pipeline, X_test, y_test)
    test_metrics["tuned"]     = args.tune
    test_metrics["high_card"] = args.high_card

    print("\nTest-set metrics:")
    for k, v in test_metrics.items():
        print(f"  {k:12s}: {v}")

    # ----------------------------------------------------------------
    # Persist
    # ----------------------------------------------------------------
    save_model(pipeline)

    try:
        from src.evaluate import log_experiment
        log_experiment(test_metrics)
        print("\nExperiment logged to results/experiments.csv")
    except NotImplementedError:
        print("\nNote: log_experiment() not yet implemented (M4 stub) — skipping CSV log")
    except Exception as exc:
        print(f"\nWarning: could not log experiment: {exc}")


if __name__ == "__main__":
    main()
