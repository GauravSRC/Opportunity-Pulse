"""Blocking: cheaply generate candidate duplicate pairs.

Blocks by canonical URL and normalized (title, org) buckets so we never run
O(n^2) similarity over the whole corpus. See docs/ml-design.md section 6.
"""

from __future__ import annotations


def canonical_url(url: str) -> str:
    """Strip tracking params / fragments for URL-equality blocking.

    TODO(phase-2): normalize scheme/host/path, drop utm_*, trailing slashes.
    """
    raise NotImplementedError("canonical_url")


def candidate_pairs(listings: list[dict]) -> list[tuple[str, str]]:
    """Return candidate id pairs to compare. TODO(phase-2)."""
    raise NotImplementedError("candidate_pairs")
