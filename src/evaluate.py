# Owner: M4
"""
Evaluation utilities: compute metrics and persist experiment results.

Public API
----------
metrics_dict(y_true, y_pred, y_proba, model_name)  → dict
log_experiment(metrics, csv_path)                  → None
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import RESULTS_DIR

_FIELDNAMES = [
    "timestamp", "model", "accuracy", "precision",
    "recall", "f1", "roc_auc", "tuned", "high_card", "notes",
]


def metrics_dict(
    y_true,
    y_pred,
    y_proba=None,
    model_name: str = "unknown",
    **extra,
) -> dict[str, Any]:
    """
    Compute classification metrics focused on the late-delivery class (label 1).

    Parameters
    ----------
    y_true     : array-like  ground-truth binary labels
    y_pred     : array-like  hard predictions (0/1)
    y_proba    : array-like, optional  predicted probability for class 1.
                 Required for roc_auc; omit if unavailable (stored as None).
    model_name : str  tag stored in the "model" field
    **extra    : additional key/value pairs merged into the returned dict
                 (e.g. tuned=True, high_card="target")

    Returns
    -------
    dict  with keys: model, accuracy, precision, recall, f1, roc_auc, …extra
    """
    # TODO M4:
    #   from sklearn.metrics import (
    #       accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    #   )
    #   m = {
    #       "model":     model_name,
    #       "accuracy":  round(accuracy_score(y_true, y_pred), 4),
    #       "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
    #       "recall":    round(recall_score(y_true, y_pred, zero_division=0), 4),
    #       "f1":        round(f1_score(y_true, y_pred, zero_division=0), 4),
    #       "roc_auc":   round(roc_auc_score(y_true, y_proba), 4) if y_proba is not None else None,
    #   }
    #   m.update(extra)
    #   return m
    raise NotImplementedError(
        "TODO M4 — compute accuracy, precision, recall, f1, roc_auc and return dict"
    )


def log_experiment(
    metrics: dict[str, Any],
    csv_path: Path | None = None,
) -> None:
    """
    Append ``metrics`` as a row in results/experiments.csv.
    Creates the file with a header row if it does not already exist.

    Parameters
    ----------
    metrics  : dict  output of metrics_dict() (or any dict with the same keys)
    csv_path : override path; defaults to RESULTS_DIR / "experiments.csv"
    """
    # TODO M4:
    #   path = csv_path or (RESULTS_DIR / "experiments.csv")
    #   path.parent.mkdir(parents=True, exist_ok=True)
    #   write_header = not path.exists() or path.stat().st_size == 0
    #   row = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    #   row.update(metrics)
    #   with open(path, "a", newline="") as fh:
    #       writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES, extrasaction="ignore")
    #       if write_header:
    #           writer.writeheader()
    #       writer.writerow(row)
    raise NotImplementedError(
        "TODO M4 — append timestamped row to results/experiments.csv"
    )
