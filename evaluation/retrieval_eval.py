"""Retrieval + rerank evaluation: Recall@k, MRR, nDCG.

Dataset: JSONL of {profile, relevant_listing_ids}. See docs/evaluation.md.
TODO(phase-6): implement metric computation against the retriever/reranker.
"""

from __future__ import annotations


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = len(set(retrieved[:k]) & relevant)
    return hits / len(relevant)


def run(dataset_path: str) -> dict:
    raise NotImplementedError("retrieval_eval.run")  # TODO(phase-6)
