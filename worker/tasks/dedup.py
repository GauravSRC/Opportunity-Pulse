"""Deduplication task — cluster + merge normalized listings."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_dedup(ctx: dict, listing_ids: list[str] | None = None) -> dict:
    """Run the full dedup pass: block → pairwise sim → cluster → merge."""
    from app.db.session import SessionLocal
    from app.services import pipeline

    db = SessionLocal()
    try:
        result = pipeline.dedup_all(db)
    finally:
        db.close()

    return result
