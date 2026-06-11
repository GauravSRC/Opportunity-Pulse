"""Merge a cluster of duplicate listings into a canonical record.

Picks the most complete record as canonical, unions skills, keeps the earliest
posted_at, and records every source URL in merged_metadata_json. Pure functions.
"""

from __future__ import annotations


def _completeness(listing: dict) -> int:
    """Heuristic richness score to pick the canonical representative."""
    score = 0
    score += len(listing.get("description") or "")
    score += 50 * len(listing.get("skills") or [])
    score += 30 if listing.get("org") else 0
    score += 30 if listing.get("posted_at") else 0
    score += 20 if listing.get("location") else 0
    return score


def choose_canonical(members: list[dict]) -> str:
    """Return the id of the richest member."""
    best = max(members, key=_completeness)
    return str(best["id"])


def merge_metadata(members: list[dict]) -> dict:
    """Union of useful fields across the cluster."""
    skills: set[str] = set()
    urls: list[str] = []
    sources: list[str] = []
    posted_dates = []
    for m in members:
        for s in m.get("skills") or []:
            skills.add(s)
        if m.get("url"):
            urls.append(m["url"])
        if m.get("source_key"):
            sources.append(m["source_key"])
        if m.get("posted_at"):
            posted_dates.append(m["posted_at"])
    return {
        "member_count": len(members),
        "union_skills": sorted(skills),
        "source_urls": sorted(set(urls)),
        "sources": sorted(set(sources)),
        "earliest_posted_at": min(posted_dates) if posted_dates else None,
    }
