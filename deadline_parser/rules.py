"""Rule-based deadline extraction (first rung): absolute dates + rolling markers.

Deterministic and dependency-light (regex + dateparser). "rolling until filled"
style phrases map to kind=rolling. Absolute dates are parsed from common formats.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from deadline_parser.confidence import ExtractionResult

ROLLING_MARKERS = (
    "rolling",
    "until filled",
    "until positions are filled",
    "open until filled",
    "reviewed on a rolling basis",
)

# Candidate absolute-date substrings (Month DD, YYYY / DD Month YYYY / ISO).
_MONTHS = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_DATE_PATTERNS = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b", re.I),
    re.compile(rf"\b{_MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b", re.I),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTHS}\s+\d{{4}}\b", re.I),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b"),
]


def _parse_date(s: str) -> datetime | None:
    try:
        import dateparser  # lazy; light dependency
    except Exception:
        return None
    dt = dateparser.parse(s, settings={"RETURN_AS_TIMEZONE_AWARE": True, "PREFER_DATES_FROM": "future"})
    if dt and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse(text: str) -> ExtractionResult:
    low = (text or "").lower()
    for marker in ROLLING_MARKERS:
        if marker in low:
            return ExtractionResult(
                kind="rolling", raw_phrase=marker, confidence=0.85, extractor="rule"
            )

    for pat in _DATE_PATTERNS:
        m = pat.search(text or "")
        if m:
            dt = _parse_date(m.group(0))
            if dt:
                return ExtractionResult(
                    kind="fixed",
                    resolved_date=dt,
                    raw_phrase=m.group(0),
                    confidence=0.9,
                    extractor="rule",
                )
    return ExtractionResult(kind="unknown", confidence=0.0, extractor="rule")
