"""Deadline extraction task — run fallback ladder over listings missing deadlines."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_deadline(ctx: dict, listing_ids: list[str] | None = None) -> dict:
    """Extract deadlines for listings that don't have one yet."""
    from app.db.session import SessionLocal
    from app.models.listing import NormalizedListing
    from app.models.deadline import Deadline
    from app.models.enums import DeadlineKind, Extractor
    from deadline_parser import extract as extract_deadline
    from sqlalchemy import select, exists
    import uuid

    db = SessionLocal()
    processed = 0
    try:
        # Find listings without a deadline row
        q = (
            select(NormalizedListing)
            .where(~exists().where(Deadline.listing_id == NormalizedListing.id))
        )
        if listing_ids:
            q = q.where(NormalizedListing.id.in_([uuid.UUID(i) for i in listing_ids]))

        listings = db.execute(q).scalars().all()
        for listing in listings:
            text = listing.description or listing.title or ""
            try:
                result = extract_deadline(text, use_llm=False)
                db.add(
                    Deadline(
                        listing_id=listing.id,
                        kind=DeadlineKind(result.kind),
                        resolved_date=result.resolved_date,
                        anchor_text=result.anchor_text,
                        raw_phrase=result.raw_phrase,
                        confidence=result.confidence,
                        needs_review=result.needs_review,
                        extractor=Extractor(result.extractor),
                    )
                )
                processed += 1
            except Exception:
                pass
        db.commit()
    finally:
        db.close()

    return {"processed": processed}
