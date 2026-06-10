"""Deadline update graph (fallback ladder).

collect_text -> rules -> (conf<theta) ner -> (conf<theta) llm -> confidence ->
persist | review_queue. LLM retried x2 -> 'unknown'. Low confidence -> human
review queue. See docs/agents.md#4-deadline-update.

TODO(phase-3): build the conditional StateGraph over agents.state.DeadlineState
calling the deadline_parser package.
"""

from __future__ import annotations

from agents.state import DeadlineState


def build_deadline_graph():
    """Return a compiled LangGraph for deadline extraction. TODO(phase-3)."""
    raise NotImplementedError("build_deadline_graph")
