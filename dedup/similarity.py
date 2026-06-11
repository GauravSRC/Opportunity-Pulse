"""Pairwise similarity: URL equality + rapidfuzz title/org + optional embedding.

Deterministic and explainable. The combined score drives clustering; the
fallback (exact canonical-URL match) guarantees we never *fail* to merge an
obvious duplicate even if fuzzy scoring is conservative.
"""

from __future__ import annotations

from rapidfuzz import fuzz

from dedup.blocker import canonical_url
from ranking.retriever import cosine

DEFAULT_MERGE_THRESHOLD = 0.82


def pair_score(a: dict, b: dict, vec_a: list[float] | None = None, vec_b: list[float] | None = None) -> dict:
    """Return {url_match, fuzzy_title, fuzzy_org, cosine, combined}.

    ``a``/``b`` need: url, title, org. Embeddings are optional; when absent the
    score relies on URL + fuzzy text only.
    """
    url_match = bool(canonical_url(a.get("url", "")) and canonical_url(a.get("url", "")) == canonical_url(b.get("url", "")))
    fuzzy_title = fuzz.token_set_ratio(a.get("title", ""), b.get("title", "")) / 100.0
    fuzzy_org = fuzz.token_set_ratio(a.get("org", "") or "", b.get("org", "") or "") / 100.0
    cos = cosine(vec_a, vec_b) if vec_a and vec_b else 0.0

    # URL match is decisive; otherwise a weighted blend (title dominates, org
    # and embedding refine).
    combined = 1.0 if url_match else 0.55 * fuzzy_title + 0.20 * fuzzy_org + 0.25 * max(0.0, cos)
    return {
        "url_match": url_match,
        "fuzzy_title": round(fuzzy_title, 4),
        "fuzzy_org": round(fuzzy_org, 4),
        "cosine": round(cos, 4),
        "combined": round(combined, 4),
    }


def is_duplicate(score: dict, threshold: float = DEFAULT_MERGE_THRESHOLD) -> bool:
    return bool(score.get("url_match")) or score.get("combined", 0.0) >= threshold
