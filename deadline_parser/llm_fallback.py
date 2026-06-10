"""LLM fallback rung (last resort) for fuzzy/anchored phrases.

Only reached when rules and NER are low-confidence. Returns a structured
ExtractionResult with a confidence the ladder uses to decide review routing.
If the LLM is unavailable, the caller keeps the best lower-rung result — the
product never blocks on the LLM.
"""

from __future__ import annotations

from deadline_parser.confidence import ExtractionResult

SYSTEM_PROMPT = (
    "Extract an application deadline from the text. Return kind "
    "(fixed|rolling|relative|unknown), an ISO date if resolvable, an anchor "
    "phrase if the deadline is relative to an event, the exact source phrase, "
    "and a confidence in [0,1]. Do not invent dates."
)


def parse(text: str) -> ExtractionResult:
    """Structured LLM extraction via agents.llm. TODO(phase-3)."""
    raise NotImplementedError("llm_fallback.parse")
