"""Normalization helpers shared across adapters.

Common work delegated here: HTML/text cleaning, skill extraction (dictionary +
alias matching), and URL canonicalization. Kept deterministic and dependency
light so adapters stay thin.
"""

from __future__ import annotations

import re

from dedup.blocker import canonical_url as _canonical_url

# Small curated skill vocabulary. canonical -> aliases. Extend over time / move
# to the `skills` table. Matching is case-insensitive on word boundaries.
SKILL_VOCAB: dict[str, list[str]] = {
    "Python": ["python", "py"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "cv"],
    "SQL": ["sql", "postgres", "postgresql"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "next.js", "nextjs"],
    "Go": ["golang"],
    "Rust": ["rust"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Docker": ["docker"],
    "Data Science": ["data science"],
    "Research": ["research", "publication", "paper"],
    "Distributed Systems": ["distributed systems"],
    "LLM": ["llm", "large language model", "transformers"],
}

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_text(html_or_text: str | None) -> str:
    """Strip markup and collapse whitespace into a plain description."""
    if not html_or_text:
        return ""
    text = html_or_text
    if "<" in text and ">" in text:
        try:
            from bs4 import BeautifulSoup

            text = BeautifulSoup(text, "html.parser").get_text(" ")
        except Exception:
            text = _TAG_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def extract_skills(text: str | None) -> list[str]:
    """Dictionary + alias skill extraction. Returns canonical skill names."""
    if not text:
        return []
    low = f" {text.lower()} "
    found: list[str] = []
    for canonical, aliases in SKILL_VOCAB.items():
        for alias in (canonical.lower(), *aliases):
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", low):
                found.append(canonical)
                break
    return sorted(set(found))


def canonicalize_url(url: str) -> str:
    """Normalize a URL for dedup/idempotency (delegates to dedup.blocker)."""
    return _canonical_url(url)
