"""Retrieval-augmented context for outreach drafting.

Gathers grounding context appropriate to the artifact type. For the MVP this is
deterministic: it draws on the listing's own structured fields and links
(lab page, paper URLs, company/program/event pages) plus the user's profile,
and reports a grounding level. Network/LLM expansion is an optional enhancement
(Phase 4+) behind the provider layer; absence never blocks drafting.
"""

from __future__ import annotations

from email_agent.router import ArtifactType

_KIND_BY_LINK = {
    "lab_page": "lab_page",
    "paper_urls": "paper",
    "apply_url": "apply_url",
    "company_page": "company_page",
    "program_page": "program_page",
    "event_page": "event_page",
}


def gather_context(listing: dict, profile: dict, artifact_type: ArtifactType) -> dict:
    """Return {sources: [{kind, url}], facts: {...}, grounding: high|medium|low}."""
    links = listing.get("links_json") or listing.get("links") or {}
    sources: list[dict] = []
    for key, url in links.items():
        if not url:
            continue
        kind = _KIND_BY_LINK.get(key, key)
        if isinstance(url, list):
            sources.extend({"kind": kind, "url": u} for u in url if u)
        else:
            sources.append({"kind": kind, "url": url})

    # Grounding reflects how much real, listing-specific context we have.
    if sources and listing.get("description"):
        grounding = "high"
    elif sources or listing.get("description"):
        grounding = "medium"
    else:
        grounding = "low"

    facts = {
        "title": listing.get("title"),
        "org": listing.get("org"),
        "type": listing.get("type"),
        "url": listing.get("url"),
        "description_excerpt": (listing.get("description") or "")[:600],
        "matched_skills": sorted(
            set(s.lower() for s in (profile.get("skills") or []))
            & set(s.lower() for s in (listing.get("skills") or []))
        ),
        "user_headline": profile.get("headline"),
        "user_name": profile.get("name") or profile.get("headline") or "Your Name",
        "user_contact": profile.get("contact") or profile.get("email") or "",
    }
    return {"sources": sources, "facts": facts, "grounding": grounding}
