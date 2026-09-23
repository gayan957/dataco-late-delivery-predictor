# Owner: M1 / M4 (collaborative)
"""
Logistic Regression baseline trainer.

CLI: python -m src.train_logreg [--cv-folds N] [--high-card {target,frequency}]

Same CLI shape and save convention as train_xgb.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.config import RANDOM_SEED, MODELS_DIR
from src.encoders import build_encoder


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train Logistic Regression baseline")
    p.add_argument("--cv-folds", type=int, default=5)
    p.add_argument("--high-card", choices=["target", "frequency"], default="target")
    return p.parse_args()


def build_pipeline(high_card_strategy: str = "target") -> Pipeline:
    """
    Returns Pipeline([("encoder", ColumnTransformer), ("clf", LogisticRegression)]).

    TODO M1/M4:
        encoder = build_encoder(high_card_strategy)
        clf = LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs",
            class_weight="balanced", random_state=RANDOM_SEED
        )
        return Pipeline([("encoder", encoder), ("clf", clf)])
    """
    raise NotImplementedError("TODO M1/M4 — build LogisticRegression pipeline")


def main():
    """
    Load split, cross-validate with StratifiedGroupKFold, fit on full train set,
    evaluate on test set, save model to models/logreg_pipeline.pkl, log experiment.

    TODO M1/M4: mirror the structure of train_xgb.main()
    """
    raise NotImplementedError("TODO M1/M4 — implement train_logreg main()")


if __name__ == "__main__":
    main()
