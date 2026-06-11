"""Decay/urgency recompute task — updates urgency scores from deadlines and posting age."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_decay(ctx: dict) -> dict:
    """Recompute urgency field on RankScore rows using deadline proximity and posting age.

    Uses simple exponential decay:  urgency = exp(-days_to_deadline / half_life)
    Rolling/unknown deadlines use posting age with a longer half-life.
    """
    from app.db.session import SessionLocal
    from app.models.ranking import RankScore
    from app.models.deadline import Deadline
    from app.models.enums import DeadlineKind
    from sqlalchemy import select
    from datetime import datetime, timezone
    import math

    FIXED_HALF_LIFE = 14.0   # days
    ROLLING_HALF_LIFE = 60.0

    db = SessionLocal()
    updated = 0
    try:
        scores = db.execute(select(RankScore)).scalars().all()
        deadlines = {
            str(d.listing_id): d
            for d in db.execute(select(Deadline)).scalars()
        }
        now = datetime.now(timezone.utc)

        for rs in scores:
            dl = deadlines.get(str(rs.listing_id))
            if dl and dl.resolved_date and dl.kind == DeadlineKind.fixed:
                days = (dl.resolved_date - now).total_seconds() / 86400
                if days < 0:
                    urgency = 0.0
                else:
                    urgency = math.exp(-days / FIXED_HALF_LIFE)
            else:
                # Rolling or unknown: decay from posted_at or created_at
                anchor = getattr(rs, "computed_at", now) or now
                if anchor.tzinfo is None:
                    anchor = anchor.replace(tzinfo=timezone.utc)
                days_old = (now - anchor).total_seconds() / 86400
                urgency = math.exp(-days_old / ROLLING_HALF_LIFE)

            components = dict(rs.components_json or {})
            components["urgency"] = round(urgency, 4)
            rs.components_json = components
            updated += 1

        db.commit()
    finally:
        db.close()

    return {"updated": updated}
