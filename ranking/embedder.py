"""Embedding helpers for profiles and opportunities.

Renders structured records into templated text, then embeds via agents.llm's
Embedder (default: local sentence-transformers). Multi-intent: one vector per
declared profile intent. See docs/ml-design.md sections 1-2.
"""

from __future__ import annotations


def render_profile_text(profile: dict, intent: str | None = None) -> str:
    """Template a profile (optionally intent-scoped) into an embedding doc.

    TODO(phase-1): headline + top skills + intent + notable projects.
    """
    raise NotImplementedError("render_profile_text")


def render_listing_text(listing: dict) -> str:
    """Template a normalized listing into an embedding doc.

    TODO(phase-1): title + org + type + skills + summary.
    """
    raise NotImplementedError("render_listing_text")


def embed_profile(profile: dict) -> dict[str, list[float]]:
    """Return {intent: vector} for each declared intent. TODO(phase-1)."""
    raise NotImplementedError("embed_profile")


def embed_listing(listing: dict) -> list[float]:
    """Return the listing vector. TODO(phase-1)."""
    raise NotImplementedError("embed_listing")
