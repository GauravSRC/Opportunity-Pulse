"""Outreach generation graph (on-demand, human-in-the-loop).

route_by_type -> retrieve_context(RAG) -> draft -> self_check ->
present_for_approval. The HITL gate interrupts before anything is saved as
approved; nothing is ever auto-sent. ``route_by_type`` produces a cold_email
ONLY for research/lab opportunities (see email_agent.router).
See docs/agents.md#5-outreach-generation-on-demand.

TODO(phase-4): build the StateGraph over agents.state.OutreachState with a
LangGraph interrupt at present_for_approval.
"""

from __future__ import annotations

from agents.state import OutreachState


def build_outreach_graph():
    """Return a compiled LangGraph for outreach. TODO(phase-4)."""
    raise NotImplementedError("build_outreach_graph")


def route_by_type(state: OutreachState) -> OutreachState: ...  # TODO(phase-4)
def retrieve_context(state: OutreachState) -> OutreachState: ...  # TODO(phase-4)
def draft(state: OutreachState) -> OutreachState: ...  # TODO(phase-4)
def self_check(state: OutreachState) -> OutreachState: ...  # TODO(phase-4)
