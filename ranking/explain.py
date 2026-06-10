"""Build the human-readable ranking explanation payload.

Consumes the stored components_json + matched skills and produces the
ExplanationOut shape used by the web "Why it matched" panel and the extension.
"""

from __future__ import annotations


def build_explanation(
    listing_id: str,
    score: float,
    components: dict[str, float],
    matched_skills: list[str],
    model_version: str,
) -> dict:
    """Return the explanation dict. TODO(phase-2): add natural-language summary."""
    return {
        "listing_id": listing_id,
        "score": score,
        "components": components,
        "matched_skills": matched_skills,
        "model_version": model_version,
    }
