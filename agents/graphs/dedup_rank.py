"""Dedup + ranking graph.

load_new -> block -> pairwise_sim -> cluster -> merge -> embed_canonical ->
retrieve -> rerank -> score -> explain -> persist. Branch: skip rerank if over
the latency budget. See docs/agents.md#3-dedup--ranking.

TODO(phase-2): build the StateGraph over agents.state.DedupRankState calling
the dedup/ and ranking/ packages.
"""

from __future__ import annotations

from agents.state import DedupRankState


def build_dedup_rank_graph():
    """Return a compiled LangGraph for dedup+ranking. TODO(phase-2)."""
    raise NotImplementedError("build_dedup_rank_graph")


def block(state: DedupRankState) -> DedupRankState: ...  # TODO(phase-2)
def cluster(state: DedupRankState) -> DedupRankState: ...  # TODO(phase-2)
def retrieve(state: DedupRankState) -> DedupRankState: ...  # TODO(phase-2)
def rerank(state: DedupRankState) -> DedupRankState: ...  # TODO(phase-2)
def score(state: DedupRankState) -> DedupRankState: ...  # TODO(phase-2)
