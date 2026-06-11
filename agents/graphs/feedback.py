"""Feedback learning graph.

collect_signals -> update_weights(online) -> (threshold) schedule_offline_retrain.
Failure keeps prior weights; exploration term guards against filter bubbles.
See docs/agents.md#6-feedback-learning.

TODO(phase-6): implement over agents.state.FeedbackState.
"""

from __future__ import annotations


def build_feedback_graph():
    """Return a compiled LangGraph for the learning loop. TODO(phase-6)."""
    raise NotImplementedError("build_feedback_graph")
