"""Deadline extraction fallback ladder: rules -> ner -> llm, with confidence.

The product never blocks on the LLM: if it is unavailable, extraction stops at
the best rules/NER result (or 'unknown'). See docs/ml-design.md section 7.
"""

from __future__ import annotations

from deadline_parser.confidence import ExtractionResult, REVIEW_THRESHOLD

__all__ = ["extract", "ExtractionResult", "REVIEW_THRESHOLD"]


def extract(text: str) -> ExtractionResult:
    """Run the full ladder and return the best result with confidence.

    TODO(phase-3): rules.parse() -> if low, ner.parse() -> if low,
    llm_fallback.parse(); set needs_review when confidence < REVIEW_THRESHOLD.
    """
    raise NotImplementedError("extract")
