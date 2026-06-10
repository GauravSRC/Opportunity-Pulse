"""Source management endpoints (admin).

TODO(phase-1/7): CRUD over opportunity_sources; show health metrics.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.feedback import SourceIn, SourceUpdate

router = APIRouter()


@router.get("")
def list_sources() -> list[dict]:
    raise HTTPException(status_code=501, detail="TODO(phase-1): list_sources")


@router.post("", status_code=201)
def create_source(payload: SourceIn) -> dict:
    raise HTTPException(status_code=501, detail="TODO(phase-1): create_source")


@router.patch("/{source_key}")
def update_source(source_key: str, payload: SourceUpdate) -> dict:
    raise HTTPException(status_code=501, detail="TODO(phase-1): update_source")
