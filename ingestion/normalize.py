"""Normalization helpers shared across adapters.

Adapters delegate common work here: URL canonicalization, skill extraction,
text cleaning, and assembling the canonical NormalizedListing.
"""

from __future__ import annotations


def clean_text(html_or_text: str) -> str:
    """Strip markup/boilerplate to a plain description. TODO(phase-1)."""
    raise NotImplementedError("clean_text")


def extract_skills(text: str) -> list[str]:
    """Extract skill tokens (dictionary + simple NER). TODO(phase-1)."""
    raise NotImplementedError("extract_skills")


def canonicalize_url(url: str) -> str:
    """Normalize a URL for dedup/idempotency. TODO(phase-1)."""
    raise NotImplementedError("canonicalize_url")
