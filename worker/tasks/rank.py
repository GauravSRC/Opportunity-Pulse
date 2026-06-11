"""Ranking task — recompute rank_scores for one user or all users."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


async def run_ranking(ctx: dict, user_id: str | None = None, intent: str | None = None) -> dict:
    """Retrieve → score → explain → persist RankScore rows for user(s)."""
    from app.db.session import SessionLocal
    from app.models.user import User
    from app.services import ranking_service
    from sqlalchemy import select
    import uuid

    db = SessionLocal()
    try:
        if user_id:
            uid = uuid.UUID(user_id)
            scored = ranking_service.rank_user(db, uid)
            return {"users": 1, "scored": scored}

        # Batch mode: rank all users
        users = db.execute(select(User)).scalars().all()
        total = 0
        for user in users:
            try:
                total += ranking_service.rank_user(db, user.id)
            except Exception:
                pass
        return {"users": len(users), "scored": total}
    finally:
        db.close()
