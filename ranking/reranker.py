"""Optional cross-encoder reranker (second stage).

Latency-gated: the dedup_rank graph skips this when over budget and uses the
retrieval order directly. See docs/ml-design.md section 4.
"""

from __future__ import annotations


def rerank(profile_text: str, candidate_ids: list[str], budget_ms: int) -> list[str]:
    """Reorder candidates with a cross-encoder; return original order on timeout.

    TODO(phase-2): load settings.reranker_model lazily; score pairs; respect
    budget_ms (the deterministic fallback is the input order).
    """
    raise NotImplementedError("rerank")
