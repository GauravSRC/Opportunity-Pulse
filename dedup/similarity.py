"""Pairwise similarity: embedding cosine + rapidfuzz title/org.

Deterministic fallback: exact URL + exact normalized-title match only.
See docs/ml-design.md section 6.
"""

from __future__ import annotations


def pair_score(a: dict, b: dict) -> dict:
    """Return {cosine, fuzzy_title, fuzzy_org, combined}. TODO(phase-2)."""
    raise NotImplementedError("pair_score")


DEFAULT_MERGE_THRESHOLD = 0.82
