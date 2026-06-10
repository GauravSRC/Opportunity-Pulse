"""Final explainable score blend.

score = w_sem*semantic + w_skill*skill_overlap + w_rec*recency + w_urg*urgency
        (+ w_fb*feedback_prior)

Every weighted contribution is returned so the UI can render "why it matched"
verbatim. Weights are per-user and updated by the feedback loop. See
docs/ml-design.md (final score blend).
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_WEIGHTS: dict[str, float] = {
    "semantic": 0.45,
    "skill_overlap": 0.25,
    "recency": 0.15,
    "urgency": 0.15,
    "feedback": 0.0,
}


@dataclass
class ScoredListing:
    listing_id: str
    score: float
    components: dict[str, float] = field(default_factory=dict)
    matched_skills: list[str] = field(default_factory=list)


def blend(
    components: dict[str, float],
    weights: dict[str, float] | None = None,
) -> tuple[float, dict[str, float]]:
    """Return (final_score, weighted_contributions).

    TODO(phase-2): validate inputs; this is the deterministic core used by both
    batch ranking and the explanation endpoint.
    """
    w = weights or DEFAULT_WEIGHTS
    contributions = {k: w.get(k, 0.0) * components.get(k, 0.0) for k in w}
    return sum(contributions.values()), contributions
