# Owner: M1 / M4 (collaborative)
"""
Decision Tree and K-Nearest Neighbours trainers.

CLI: python -m src.train_tree_knn --model {tree,knn}
                                   [--tune] [--cv-folds N]
                                   [--high-card {target,frequency}]

Same CLI shape and save convention as train_xgb.py.
"""
from __future__ import annotations

import argparse

from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.config import RANDOM_SEED
from src.encoders import build_encoder


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train Decision Tree or KNN")
    p.add_argument(
        "--model", choices=["tree", "knn"], default="tree",
        help="Which model to train",
    )
    p.add_argument("--tune", action="store_true")
    p.add_argument("--cv-folds", type=int, default=5)
    p.add_argument("--n-iter", type=int, default=20)
    p.add_argument("--high-card", choices=["target", "frequency"], default="target")
    return p.parse_args()


def build_tree_pipeline(high_card_strategy: str = "target") -> Pipeline:
    """
    Returns Pipeline([("encoder", ...), ("clf", DecisionTreeClassifier)]).

    TODO M1/M4:
        encoder = build_encoder(high_card_strategy)
        clf = DecisionTreeClassifier(
            max_depth=10, class_weight="balanced", random_state=RANDOM_SEED
        )
        return Pipeline([("encoder", encoder), ("clf", clf)])
    """
    raise NotImplementedError("TODO M1/M4 — build DecisionTree pipeline")


def build_knn_pipeline(high_card_strategy: str = "target") -> Pipeline:
    """
    Returns Pipeline([("encoder", ...), ("scaler", StandardScaler), ("clf", KNN)]).

    Note: KNN is distance-based, so features must be scaled after encoding.

    TODO M1/M4:
        encoder = build_encoder(high_card_strategy)
        scaler  = StandardScaler()
        clf     = KNeighborsClassifier(n_neighbors=15, weights="distance", n_jobs=-1)
        return Pipeline([("encoder", encoder), ("scaler", scaler), ("clf", clf)])
    """
    raise NotImplementedError("TODO M1/M4 — build KNN pipeline (include StandardScaler)")


def main():
    """
    Dispatcher: train either Decision Tree or KNN based on --model flag.

    TODO M1/M4: parse args, select pipeline, cross-validate, fit, evaluate, save.
        Tune spaces:
            tree: max_depth [3,5,10,None], min_samples_leaf [1,5,10]
            knn:  n_neighbors [5,10,15,25,50], weights ["uniform","distance"]
    """
    raise NotImplementedError("TODO M1/M4 — implement train_tree_knn main()")


if __name__ == "__main__":
    main()
