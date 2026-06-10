"""Deduplication task — cluster + merge new normalized listings."""

from __future__ import annotations


async def run_dedup(ctx: dict, listing_ids: list[str] | None = None) -> dict:
    """TODO(phase-2): run the dedup stage (block -> sim -> cluster -> merge)."""
    raise NotImplementedError("run_dedup")
