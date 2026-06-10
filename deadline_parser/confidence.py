"""Shared result type + confidence threshold for the deadline ladder."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# Below this confidence, a deadline is routed to the human review queue.
REVIEW_THRESHOLD = 0.6


@dataclass
class ExtractionResult:
    kind: str  # fixed | rolling | relative | unknown
    resolved_date: datetime | None = None
    anchor_text: str | None = None
    raw_phrase: str | None = None
    confidence: float = 0.0
    extractor: str = "rule"  # rule | ner | llm

    @property
    def needs_review(self) -> bool:
        return self.confidence < REVIEW_THRESHOLD
