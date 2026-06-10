"""Dedup evaluation: pairwise Precision/Recall/F1 + cluster purity.

Dataset: JSONL of labeled duplicate/non-duplicate pairs. See docs/evaluation.md.
TODO(phase-6): implement against dedup.similarity + dedup.cluster.
"""

from __future__ import annotations


def prf1(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def run(dataset_path: str) -> dict:
    raise NotImplementedError("dedup_eval.run")  # TODO(phase-6)
