"""Relative / fuzzy phrase handling (second rung).

Examples:
  - "within 7 days of announcement"     -> resolved relative to reference date
  - "in two weeks"                       -> resolved
  - "end of quarter" / "end of month"    -> resolved
  - "two weeks before demo day"          -> anchored: store anchor_text, no date
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from deadline_parser.confidence import ExtractionResult

_WORD_NUM = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
_UNIT_DAYS = {"day": 1, "days": 1, "week": 7, "weeks": 7, "month": 30, "months": 30}

_WITHIN = re.compile(
    r"\b(?:within|in)\s+(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(day|days|week|weeks|month|months)\b",
    re.I,
)
_BEFORE_ANCHOR = re.compile(
    r"\b(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(day|days|week|weeks|month|months)\s+(?:before|prior to)\s+([a-z][a-z \-]{2,40})",
    re.I,
)
_END_OF = re.compile(r"\bend of (the )?(month|quarter|year)\b", re.I)


def _num(token: str) -> int:
    token = token.lower()
    return int(token) if token.isdigit() else _WORD_NUM.get(token, 1)


def _end_of(period: str, ref: datetime) -> datetime:
    if period == "month":
        nxt = (ref.replace(day=28) + timedelta(days=4)).replace(day=1)
        return nxt - timedelta(days=1)
    if period == "quarter":
        q_end_month = ((ref.month - 1) // 3 + 1) * 3
        nxt = ref.replace(month=q_end_month, day=28) + timedelta(days=4)
        return nxt.replace(day=1) - timedelta(days=1)
    return ref.replace(month=12, day=31)


def parse(text: str, reference: datetime | None = None) -> ExtractionResult:
    ref = reference or datetime.now(timezone.utc)
    text = text or ""

    m = _BEFORE_ANCHOR.search(text)
    if m:
        anchor = m.group(3).strip().rstrip(".")
        return ExtractionResult(
            kind="relative",
            resolved_date=None,
            anchor_text=anchor,
            raw_phrase=m.group(0).strip(),
            confidence=0.55,
            extractor="rule",
        )

    m = _WITHIN.search(text)
    if m:
        days = _num(m.group(1)) * _UNIT_DAYS[m.group(2).lower()]
        return ExtractionResult(
            kind="relative",
            resolved_date=ref + timedelta(days=days),
            raw_phrase=m.group(0).strip(),
            confidence=0.7,
            extractor="rule",
        )

    m = _END_OF.search(text)
    if m:
        return ExtractionResult(
            kind="relative",
            resolved_date=_end_of(m.group(2).lower(), ref),
            raw_phrase=m.group(0).strip(),
            confidence=0.6,
            extractor="rule",
        )

    return ExtractionResult(kind="unknown", confidence=0.0, extractor="rule")
