"""Embedding helpers for profiles and opportunities.

Renders structured records into templated text, then embeds via the provider
layer in ``agents.llm`` (deterministic hashing by default; sentence-transformers
when configured). Multi-intent: one vector per declared profile intent.
"""

from __future__ import annotations

from agents.llm import get_embedder


def render_profile_text(profile: dict, intent: str | None = None) -> str:
    """Template a profile (optionally intent-scoped) into an embedding doc."""
    parts: list[str] = []
    if intent:
        parts.append(f"Looking for {intent} opportunities.")
    if profile.get("headline"):
        parts.append(str(profile["headline"]))
    skills = profile.get("skills") or []
    if skills:
        parts.append("Skills: " + ", ".join(skills))
    locations = profile.get("locations") or []
    if locations:
        parts.append("Locations: " + ", ".join(locations))
    exp = profile.get("experience_json") or profile.get("experience") or {}
    if isinstance(exp, dict) and exp.get("summary"):
        parts.append(str(exp["summary"]))
    return " ".join(parts).strip() or "general opportunities"


def render_listing_text(listing: dict) -> str:
    """Template a normalized listing into an embedding doc."""
    parts = [
        str(listing.get("title") or ""),
        str(listing.get("org") or ""),
        str(listing.get("type") or ""),
    ]
    skills = listing.get("skills") or []
    if skills:
        parts.append("Skills: " + ", ".join(skills))
    if listing.get("description"):
        parts.append(str(listing["description"])[:2000])
    return " ".join(p for p in parts if p).strip() or "opportunity"


def embed_profile(profile: dict) -> dict[str, list[float]]:
    """Return {intent: vector}. Always includes a default '_all' vector."""
    embedder = get_embedder()
    intents = profile.get("intents") or []
    out: dict[str, list[float]] = {"_all": embedder.embed_one(render_profile_text(profile))}
    for intent in intents:
        out[intent] = embedder.embed_one(render_profile_text(profile, intent))
    return out


def embed_listing(listing: dict) -> list[float]:
    """Return the listing vector."""
    return get_embedder().embed_one(render_listing_text(listing))
