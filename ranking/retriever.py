"""Candidate retrieval / similarity.

MVP retrieval computes cosine similarity in Python over stored vectors (works
identically on Postgres+pgvector and SQLite). The pgvector HNSW index is the
production performance path; the math here is the source of truth.
"""

from __future__ import annotations

import math


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity in [-1, 1]; vectors may or may not be pre-normalized."""
    # Explicit None/length checks (not `not a or not b`): a numpy vector would
    # make a bare truth-test raise "truth value of an array ... is ambiguous".
    if a is None or b is None or len(a) != len(b) or len(a) == 0:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def top_k(query: list[float], candidates: dict[str, list[float]], k: int = 100) -> list[tuple[str, float]]:
    """Return [(id, similarity)] sorted desc, truncated to k."""
    scored = [(cid, cosine(query, vec)) for cid, vec in candidates.items()]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Fuse multiple ranked id lists (dense + lexical) via RRF."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return [cid for cid, _ in sorted(scores.items(), key=lambda t: t[1], reverse=True)]
