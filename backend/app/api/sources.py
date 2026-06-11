"""Source management endpoints + ingest/rank triggers."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.feedback import SourceIn, SourceUpdate
from app.services import pipeline, source_service

router = APIRouter()


def _source_out(s) -> dict:
    return {
        "key": s.key,
        "name": s.name,
        "category": s.category,
        "access_method": s.access_method.value,
        "base_url": s.base_url,
        "enabled": s.enabled,
        "health": s.health_json or {},
        "last_run_at": s.last_run_at,
    }


@router.get("")
def list_sources(db: Session = Depends(get_db)) -> list[dict]:
    return [_source_out(s) for s in source_service.list_sources(db)]


@router.post("", status_code=201)
def create_source(payload: SourceIn, db: Session = Depends(get_db)) -> dict:
    from app.models.enums import AccessMethod
    from app.models.source import OpportunitySource

    existing = source_service.get_source(db, payload.key)
    if existing:
        raise HTTPException(status_code=409, detail=f"Source '{payload.key}' already exists")
    source = OpportunitySource(
        key=payload.key,
        name=payload.name,
        category=payload.category,
        access_method=AccessMethod(payload.access_method.value),
        base_url=payload.base_url,
        config_json=payload.config,
        enabled=payload.enabled,
        health_json={},
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return _source_out(source)


@router.patch("/{source_key}")
def update_source(source_key: str, payload: SourceUpdate, db: Session = Depends(get_db)) -> dict:
    source = source_service.get_source(db, source_key)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    if payload.enabled is not None:
        source.enabled = payload.enabled
    if payload.config is not None:
        source.config_json = {**(source.config_json or {}), **payload.config}
    db.commit()
    db.refresh(source)
    return _source_out(source)


@router.post("/sync")
def sync_registry(db: Session = Depends(get_db)) -> dict:
    """Upsert sources from registry.yaml into the database."""
    n = source_service.sync_registry(db)
    return {"synced": n}


@router.post("/{source_key}/ingest")
def trigger_ingest(source_key: str, db: Session = Depends(get_db)) -> dict:
    """Trigger an immediate synchronous ingest for one source (dev/admin use)."""
    source = source_service.get_source(db, source_key)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    try:
        result = asyncio.get_event_loop().run_until_complete(
            pipeline.run_source(db, source)
        )
        return result
    except RuntimeError:
        # No running event loop — create a new one
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(pipeline.run_source(db, source))
        finally:
            loop.close()
        return result


@router.post("/ingest-all")
def trigger_ingest_all(db: Session = Depends(get_db)) -> dict:
    """Trigger ingest for all enabled sources."""
    sources = [s for s in source_service.list_sources(db) if s.enabled]
    results = []
    for source in sources:
        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(pipeline.run_source(db, source))
            loop.close()
            results.append(result)
        except Exception as exc:
            results.append({"source": source.key, "error": str(exc)})
    return {"results": results, "total": len(results)}


@router.post("/dedup")
def trigger_dedup(db: Session = Depends(get_db)) -> dict:
    """Run deduplication across all normalized listings."""
    return pipeline.dedup_all(db)
