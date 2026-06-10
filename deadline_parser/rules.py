"""Rule-based deadline extraction (first rung).

Handles absolute dates (via dateparser) and common patterns. "rolling until
filled" / "until positions are filled" -> kind=rolling. See relative.py for
relative phrase handling.
"""

from __future__ import annotations

from deadline_parser.confidence import ExtractionResult

ROLLING_MARKERS = (
    "rolling",
    "until filled",
    "until positions are filled",
    "open until filled",
)


def parse(text: str) -> ExtractionResult:
    """Deterministic absolute/rolling extraction. TODO(phase-3)."""
    raise NotImplementedError("rules.parse")
