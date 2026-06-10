"""robots.txt checking (cached) for any non-API fetch.

API/ATS adapters are exempt (we use sanctioned endpoints); RSS/sitemap/search/
browser adapters MUST consult this before fetching a page. See docs/sourcing.md
(legal/ethical).
"""

from __future__ import annotations


async def can_fetch(url: str, user_agent: str) -> bool:
    """Return True if robots.txt permits fetching ``url`` for ``user_agent``.

    TODO(phase-1): fetch + cache robots.txt per host; default to deny on
    ambiguity for non-API sources.
    """
    raise NotImplementedError("can_fetch")
