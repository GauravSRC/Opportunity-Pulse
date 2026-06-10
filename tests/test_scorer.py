"""Tests for the explainable score blend (deterministic core)."""

from __future__ import annotations

from ranking.scorer import DEFAULT_WEIGHTS, blend


def test_blend_returns_weighted_contributions():
    components = {
        "semantic": 1.0,
        "skill_overlap": 1.0,
        "recency": 1.0,
        "urgency": 1.0,
        "feedback": 1.0,
    }
    total, contributions = blend(components)
    # With all components = 1.0, total equals the sum of the weights.
    assert abs(total - sum(DEFAULT_WEIGHTS.values())) < 1e-9
    assert contributions["semantic"] == DEFAULT_WEIGHTS["semantic"]


def test_missing_component_treated_as_zero():
    total, contributions = blend({"semantic": 1.0})
    assert total == DEFAULT_WEIGHTS["semantic"]
    assert contributions["urgency"] == 0.0
