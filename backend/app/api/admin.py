"""Admin monitoring + rank-trigger endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import ranking_service, source_service

router = APIRouter()


@router.get("/health")
def admin_health(db: Session = Depends(get_db)) -> dict:
    """Aggregate pipeline status, source health, and eval snapshot."""
    sources = source_service.list_sources(db)
    enabled = sum(1 for s in sources if s.enabled)
    disabled = sum(1 for s in sources if not s.enabled)
    flapping = sum(
        1 for s in sources
        if (s.health_json or {}).get("consecutive_failures", 0) >= 3
    )
    source_health = [
        {
            "key": s.key,
            "enabled": s.enabled,
            "last_run_at": s.last_run_at,
            "health": s.health_json or {},
        }
        for s in sources
    ]
    return {
        "pipeline": {"status": "ok"},
        "sources": {
            "enabled": enabled,
            "disabled": disabled,
            "flapping": flapping,
            "detail": source_health,
        },
        "eval": {"last_run": None},
    }


@router.post("/rank/{user_id}")
def trigger_rank(user_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    """Recompute rank scores for a user (admin/dev)."""
    try:
        n = ranking_service.rank_user(db, user_id)
        return {"ok": True, "scored": n}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
