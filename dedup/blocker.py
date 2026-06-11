"""Blocking: cheaply generate candidate duplicate pairs.

Blocks by canonical URL and a normalized (title, org) key so we never run
O(n^2) similarity over the whole corpus. See docs/ml-design.md section 6.
"""

from __future__ import annotations

import re
from itertools import combinations
from urllib.parse import urlparse, urlunparse

_TRACKING_PREFIXES = ("utm_", "ref", "source", "fbclid", "gclid")
_WS = re.compile(r"\s+")
_NONWORD = re.compile(r"[^a-z0-9 ]+")


def canonical_url(url: str) -> str:
    """Strip scheme noise, query tracking params, and trailing slashes."""
    if not url:
        return ""
    try:
        p = urlparse(url.strip())
    except ValueError:
        return url.strip().lower()
    netloc = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/")
    return urlunparse(("https", netloc, path, "", "", "")).lower()


def title_org_key(title: str, org: str | None) -> str:
    """A coarse blocking key from normalized title + org."""
    t = _NONWORD.sub(" ", (title or "").lower())
    o = _NONWORD.sub(" ", (org or "").lower())
    return _WS.sub(" ", f"{t} {o}").strip()


def candidate_pairs(listings: list[dict]) -> list[tuple[str, str]]:
    """Return candidate id pairs that share a blocking key.

    Each listing dict needs: id, url, title, org.
    """
    by_url: dict[str, list[str]] = {}
    by_key: dict[str, list[str]] = {}
    for ls in listings:
        lid = str(ls["id"])
        cu = canonical_url(ls.get("url", ""))
        if cu:
            by_url.setdefault(cu, []).append(lid)
        key = title_org_key(ls.get("title", ""), ls.get("org"))
        if key:
            by_key.setdefault(key, []).append(lid)

    pairs: set[tuple[str, str]] = set()
    for bucket in (*by_url.values(), *by_key.values()):
        for a, b in combinations(sorted(set(bucket)), 2):
            pairs.add((a, b))
    return sorted(pairs)
