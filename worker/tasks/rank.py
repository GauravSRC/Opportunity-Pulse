"""Ranking task — recompute rank_scores for a user (or batch)."""

from __future__ import annotations


async def run_ranking(ctx: dict, user_id: str, intent: str | None = None) -> dict:
    """TODO(phase-1/2): retrieve -> rerank -> score -> explain -> persist."""
    raise NotImplementedError("run_ranking")
