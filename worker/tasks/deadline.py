"""Deadline extraction task — run the fallback ladder over new listings."""

from __future__ import annotations


async def run_deadline(ctx: dict, listing_ids: list[str] | None = None) -> dict:
    """TODO(phase-3): rules -> ner -> llm; low confidence -> review queue."""
    raise NotImplementedError("run_deadline")
