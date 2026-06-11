"""Feedback-driven ranking weight updates.

Per-user weights over the score components are nudged by feedback signals: a
positive signal (save/apply/thumbs_up/click) increases the weight of components
that were strong for that listing; a negative signal (dismiss/thumbs_down)
decreases them. Weights are renormalized and clamped, with a floor so no
component is ever fully eliminated (preserves exploration / avoids filter
bubbles). Deterministic and explainable — no opaque model.
"""

from __future__ import annotations

from ranking.scorer import DEFAULT_WEIGHTS

COMPONENTS = ("semantic", "skill_overlap", "recency", "urgency")
_FLOOR = 0.05
_LR = 0.10  # learning rate per feedback event

_SIGNAL_DIRECTION = {
    "save": 1.0,
    "applied": 1.0,
    "thumbs_up": 1.0,
    "click": 0.4,
    "dismiss": -1.0,
    "thumbs_down": -1.0,
}


def update_weights(
    weights: dict[str, float],
    signal: str,
    components: dict[str, float],
) -> dict[str, float]:
    """Return new weights after one feedback event.

    ``components`` are the (already weighted-or-raw) component values the user
    reacted to; their relative magnitude attributes credit/blame.
    """
    direction = _SIGNAL_DIRECTION.get(signal, 0.0)
    w = {c: float(weights.get(c, DEFAULT_WEIGHTS.get(c, 0.0))) for c in COMPONENTS}
    if direction == 0.0:
        return _normalize(w)

    comp_total = sum(abs(components.get(c, 0.0)) for c in COMPONENTS) or 1.0
    for c in COMPONENTS:
        attribution = abs(components.get(c, 0.0)) / comp_total
        w[c] = max(_FLOOR, w[c] + _LR * direction * attribution)
    return _normalize(w)


def _normalize(w: dict[str, float]) -> dict[str, float]:
    total = sum(w.values()) or 1.0
    return {c: round(v / total, 6) for c, v in w.items()}


def default_weights() -> dict[str, float]:
    return {c: DEFAULT_WEIGHTS[c] for c in COMPONENTS}
