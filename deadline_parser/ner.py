"""spaCy NER / pattern-matcher rung (second rung).

Finds DATE entities and nearby anchor nouns when rules are low-confidence.
"""

from __future__ import annotations

from deadline_parser.confidence import ExtractionResult


def parse(text: str) -> ExtractionResult:
    """NER-based extraction. TODO(phase-3): load spaCy model lazily."""
    raise NotImplementedError("ner.parse")
