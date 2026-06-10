"""Candidate retrieval: dense (pgvector) + lexical (BM25), with fusion.

Fallback: lexical-only when the vector index is unavailable. See
docs/ml-design.md section 3.
"""

from __future__ import annotations


def retrieve_dense(profile_vector: list[float], k: int = 100) -> list[str]:
    """Top-k normalized_listing ids by cosine over pgvector. TODO(phase-1)."""
    raise NotImplementedError("retrieve_dense")


def retrieve_lexical(query_terms: list[str], k: int = 100) -> list[str]:
    """BM25/lexical fallback channel. TODO(phase-1)."""
    raise NotImplementedError("retrieve_lexical")


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Fuse multiple ranked id lists. TODO(phase-2)."""
    raise NotImplementedError("reciprocal_rank_fusion")
