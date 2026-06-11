"""Discovery/ingestion task — fetches + normalizes all enabled sources."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session


async def run_discovery(ctx: dict, source_keys: list[str] | None = None) -> dict:
    """Fetch + normalize listings for the given (or all enabled) sources."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

    from app.db.session import SessionLocal
    from app.models.source import OpportunitySource
    from app.services import pipeline

    db: Session = SessionLocal()
    results = []
    try:
        q = select(OpportunitySource).where(OpportunitySource.enabled == True)  # noqa: E712
        if source_keys:
            q = q.where(OpportunitySource.key.in_(source_keys))
        sources = db.execute(q).scalars().all()
        for source in sources:
            result = await pipeline.run_source(db, source)
            results.append(result)
    finally:
        db.close()

    total_created = sum(r.get("created", 0) for r in results)
    total_errors = sum(r.get("errors", 0) for r in results)
    return {"sources_run": len(results), "created": total_created, "errors": total_errors, "detail": results}
