"""Deterministic ranking feature computations.

These produce the named score components (semantic, skill_overlap, recency,
urgency) that the blend in scorer.py combines and the explanation surfaces.
All are pure functions in [0, 1].
"""

from __future__ import annotations

import math
from datetime import datetime, timezone


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def skill_overlap(profile_skills: list[str], listing_skills: list[str]) -> tuple[float, list[str]]:
    """Jaccard-ish overlap of skills. Returns (score, matched_skill_names)."""
    p = {s.strip().lower() for s in profile_skills if s and s.strip()}
    l = {s.strip().lower() for s in listing_skills if s and s.strip()}
    if not p or not l:
        return 0.0, []
    matched = sorted(p & l)
    score = len(matched) / len(p | l)
    return score, matched


def recency(posted_at: datetime | None, now: datetime | None = None, half_life_days: float = 21.0) -> float:
    """Exponential recency decay on posting age. Unknown posting -> neutral 0.5."""
    if posted_at is None:
        return 0.5
    age_days = max(0.0, (_now(now) - _aware(posted_at)).total_seconds() / 86400.0)
    return math.exp(-math.log(2) * age_days / half_life_days)


def urgency(
    kind: str | None,
    resolved_date: datetime | None,
    now: datetime | None = None,
    window_days: float = 30.0,
) -> float:
    """Urgency in [0,1]: higher as a fixed deadline nears.

    - fixed/relative with a date: ramps toward 1.0 as the deadline approaches
      within ``window_days``; already-passed deadlines -> 0.0.
    - rolling: steady moderate urgency (0.6) — could close any time.
    - unknown/no date: neutral 0.4.
    """
    if kind == "rolling":
        return 0.6
    if resolved_date is None:
        return 0.4
    days_left = (_aware(resolved_date) - _now(now)).total_seconds() / 86400.0
    if days_left < 0:
        return 0.0
    if days_left >= window_days:
        return 0.2
    # linear ramp from 0.2 (far) to 1.0 (due now)
    return 1.0 - 0.8 * (days_left / window_days)
