"""Per-artifact draft generators.

Each generator consumes RAG context + profile and produces a draft. A shared
self-check verifies claims are grounded (no invented papers/affiliations).
TODO(phase-4): implement cold_email, cover_letter, sop, team_pitch, proposal,
referral_note generators that render templates/ with agents.llm.
"""

from __future__ import annotations

from email_agent.router import ArtifactType


def generate(artifact_type: ArtifactType, context: dict, profile: dict) -> dict:
    """Return {subject?, body, grounding}. TODO(phase-4)."""
    raise NotImplementedError("generate")


def self_check(draft: dict, context: dict) -> dict:
    """Flag ungrounded claims; downgrade grounding accordingly. TODO(phase-4)."""
    raise NotImplementedError("self_check")
