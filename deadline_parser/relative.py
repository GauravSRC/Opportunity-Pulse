"""Relative / fuzzy phrase handling.

Examples this targets:
  - "within 7 days of announcement"
  - "end of quarter"
  - "two weeks before demo day"   (anchored to an event -> store anchor_text)

Resolves against a reference date where possible; otherwise emits kind=relative
with anchor_text set and resolved_date left null (needs_anchor).
"""

from __future__ import annotations

from datetime import datetime

from deadline_parser.confidence import ExtractionResult


def parse(text: str, reference: datetime | None = None) -> ExtractionResult:
    """Resolve relative phrases. TODO(phase-3)."""
    raise NotImplementedError("relative.parse")
