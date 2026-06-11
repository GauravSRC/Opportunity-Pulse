"""Normalize task — recovery pass for raw listings stuck in 'new' status.

Normalization runs inline during ingest (pipeline.run_source). This task
re-queues any raw listings that were left un-normalized due to transient errors.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_normalize(ctx: dict, raw_ids: list[str] | None = None) -> dict:
    """Mark un-normalized raw listings as error so they surface in health dashboard."""
    from app.db.session import SessionLocal
    from app.models.enums import RawStatus
    from app.models.listing import RawListing
    from sqlalchemy import select

    db = SessionLocal()
    try:
        q = select(RawListing).where(RawListing.status == RawStatus.new)
        if raw_ids:
            q = q.where(RawListing.id.in_(raw_ids))
        pending = db.execute(q).scalars().all()
        for raw in pending:
            raw.status = RawStatus.error
        db.commit()
        count = len(pending)
    finally:
        db.close()

    return {"requeued": count}
