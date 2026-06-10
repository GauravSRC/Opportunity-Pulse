"""Outreach evaluation: LLM-judge rubric (relevance, grounding, tone, specificity)
plus a hook for human review samples.

See docs/evaluation.md. TODO(phase-6): implement the judge prompt + scoring and
the grounding check (no invented facts).
"""

from __future__ import annotations

RUBRIC = ["relevance", "grounding", "tone", "specificity"]


def run(judge: str = "claude") -> dict:
    raise NotImplementedError("email_eval.run")  # TODO(phase-6)
