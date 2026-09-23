# Owner: M1 / M4 (collaborative)
"""
Random Forest trainer.

CLI: python -m src.train_rf [--tune] [--cv-folds N] [--high-card {target,frequency}]

Same CLI shape and save convention as train_xgb.py.
"""
from __future__ import annotations

import argparse

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.config import RANDOM_SEED
from src.encoders import build_encoder


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train Random Forest")
    p.add_argument("--tune", action="store_true", help="Run RandomizedSearchCV")
    p.add_argument("--cv-folds", type=int, default=5)
    p.add_argument("--n-iter", type=int, default=20)
    p.add_argument("--high-card", choices=["target", "frequency"], default="target")
    return p.parse_args()


def build_pipeline(high_card_strategy: str = "target") -> Pipeline:
    """
    Returns Pipeline([("encoder", ColumnTransformer), ("clf", RandomForestClassifier)]).

    TODO M1/M4:
        encoder = build_encoder(high_card_strategy)
        clf = RandomForestClassifier(
            n_estimators=300, max_depth=None,
            class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1
        )
        return Pipeline([("encoder", encoder), ("clf", clf)])
    """
    raise NotImplementedError("TODO M1/M4 — build RandomForest pipeline")


def main():
    """
    Load split, cross-validate, optionally tune, fit, evaluate, save, log.

    TODO M1/M4:
        Tune space suggestion:
            n_estimators: [100, 300, 500]
            max_depth:    [None, 10, 20]
            min_samples_split: [2, 5, 10]
            max_features: ["sqrt", "log2"]
    """
    raise NotImplementedError("TODO M1/M4 — implement train_rf main()")


if __name__ == "__main__":
    main()
