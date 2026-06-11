"""Date-NER rung (third rung).

Uses spaCy DATE entities when the model is installed; otherwise a lightweight
regex pass that catches loose date mentions the rules rung may have missed.
Always cheap to call and never raises.
"""

from __future__ import annotations

import contextlib
import re
from datetime import UTC

from deadline_parser.confidence import ExtractionResult

_LOOSE_DATE = re.compile(
    r"\b(?:\d{1,2}\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    r"(?:\s+\d{1,2})?(?:,?\s+\d{4})?\b",
    re.I,
)


def parse(text: str) -> ExtractionResult:
    # Optional spaCy path (presence check only; model load is heavy).
    with contextlib.suppress(Exception):
        import spacy  # noqa: F401

    m = _LOOSE_DATE.search(text or "")
    if not m:
        return ExtractionResult(kind="unknown", confidence=0.0, extractor="ner")

    try:
        import dateparser

        dt = dateparser.parse(
            m.group(0), settings={"RETURN_AS_TIMEZONE_AWARE": True, "PREFER_DATES_FROM": "future"}
        )
    except Exception:
        dt = None
    if dt:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        # Lower confidence than the rules rung: looser match, may lack a year.
        conf = 0.6 if re.search(r"\d{4}", m.group(0)) else 0.45
        return ExtractionResult(
            kind="fixed", resolved_date=dt, raw_phrase=m.group(0).strip(), confidence=conf, extractor="ner"
        )
    return ExtractionResult(kind="unknown", confidence=0.0, extractor="ner")
