"""Deadline extraction fallback ladder: rules -> relative -> ner -> llm.

The product never blocks on the LLM: if it is unavailable, extraction stops at
the best deterministic result (or 'unknown'). Confidence below REVIEW_THRESHOLD
routes the deadline to the human review queue. See docs/ml-design.md section 7.
"""

from __future__ import annotations

from deadline_parser import llm_fallback, ner, relative, rules
from deadline_parser.confidence import REVIEW_THRESHOLD, ExtractionResult

__all__ = ["extract", "ExtractionResult", "REVIEW_THRESHOLD"]


def extract(text: str, *, use_llm: bool = True) -> ExtractionResult:
    """Run the ladder and return the best result, by confidence.

    Stops early once a result clears REVIEW_THRESHOLD. ``use_llm=False`` keeps it
    fully deterministic (used in tests and offline demos).
    """
    best = ExtractionResult(kind="unknown", confidence=0.0, extractor="rule")

    for rung in (rules.parse, relative.parse, ner.parse):
        result = rung(text)
        if result.confidence > best.confidence:
            best = result
        if best.confidence >= REVIEW_THRESHOLD and best.kind != "unknown":
            return best

    if use_llm and best.confidence < REVIEW_THRESHOLD:
        result = llm_fallback.parse(text)
        if result.confidence > best.confidence:
            best = result
    return best
