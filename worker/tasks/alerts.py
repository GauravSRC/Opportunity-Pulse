"""Alert evaluation + dispatch task.

Evaluates alert rules (high fit + near deadline) and creates pending Alert rows.
Actual delivery (email/in-app) is handled by the notification layer; this task
only generates the records.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_alerts(ctx: dict) -> dict:
    """Eval rules → create Alert rows for high-fit opportunities near their deadline."""
    from app.db.session import SessionLocal
    from app.models.ranking import RankScore
    from app.models.deadline import Deadline
    from app.models.alert import Alert
    from app.models.enums import AlertChannel, AlertStatus, DeadlineKind
    from sqlalchemy import select, and_
    from datetime import datetime, timezone, timedelta

    SCORE_THRESHOLD = 0.65
    DAYS_WINDOW = 7

    db = SessionLocal()
    created = 0
    try:
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=DAYS_WINDOW)

        # Find high-scoring listings
        high_scores = db.execute(
            select(RankScore).where(RankScore.score >= SCORE_THRESHOLD)
        ).scalars().all()

        # Map listing_id → deadline
        listing_ids = [rs.listing_id for rs in high_scores]
        deadlines = {}
        if listing_ids:
            for dl in db.execute(
                select(Deadline).where(Deadline.listing_id.in_(listing_ids))
            ).scalars():
                deadlines[dl.listing_id] = dl

        for rs in high_scores:
            dl = deadlines.get(rs.listing_id)
            urgent = (
                dl is not None
                and dl.kind == DeadlineKind.fixed
                and dl.resolved_date is not None
                and dl.resolved_date <= cutoff
            )
            if not urgent:
                continue

            # Skip if alert already exists for this user+listing
            existing = db.execute(
                select(Alert).where(
                    and_(
                        Alert.user_id == rs.user_id,
                        Alert.listing_id == rs.listing_id,
                        Alert.status == AlertStatus.pending,
                    )
                )
            ).first()
            if existing:
                continue

            db.add(
                Alert(
                    user_id=rs.user_id,
                    listing_id=rs.listing_id,
                    rule=f"score>={SCORE_THRESHOLD:.0%}+deadline<={DAYS_WINDOW}d",
                    channel=AlertChannel.inapp,
                    scheduled_for=now,
                    status=AlertStatus.pending,
                )
            )
            created += 1

        db.commit()
    finally:
        db.close()

    return {"alerts_created": created}
