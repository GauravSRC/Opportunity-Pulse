"""LLM fallback rung (last resort) for fuzzy/anchored phrases.

Only reached when rules and NER are low-confidence. If no chat provider is
configured/reachable, returns an 'unknown' result so the caller keeps the best
lower-rung result — the product never blocks on the LLM.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from deadline_parser.confidence import ExtractionResult

SYSTEM_PROMPT = (
    "Extract an application deadline from the text. Respond with ONLY a JSON "
    'object: {"kind": "fixed|rolling|relative|unknown", "date": "YYYY-MM-DD" or '
    'null, "anchor": string or null, "phrase": string, "confidence": 0..1}. '
    "Do not invent dates; if unsure use kind=unknown."
)


def parse(text: str) -> ExtractionResult:
    try:
        from agents.llm import LLMUnavailable, get_llm

        llm = get_llm()
        raw = llm.complete(text or "", system=SYSTEM_PROMPT, max_tokens=200)
    except Exception:  # LLMUnavailable or provider/SDK error
        return ExtractionResult(kind="unknown", confidence=0.0, extractor="llm")

    try:
        data = json.loads(raw[raw.index("{") : raw.rindex("}") + 1])
    except Exception:
        return ExtractionResult(kind="unknown", confidence=0.0, extractor="llm")

    resolved = None
    if data.get("date"):
        try:
            resolved = datetime.fromisoformat(str(data["date"])).replace(tzinfo=timezone.utc)
        except ValueError:
            resolved = None
    return ExtractionResult(
        kind=str(data.get("kind", "unknown")),
        resolved_date=resolved,
        anchor_text=data.get("anchor"),
        raw_phrase=data.get("phrase") or (text or "")[:120],
        confidence=float(data.get("confidence", 0.5)),
        extractor="llm",
    )
