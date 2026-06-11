"""Outreach generation endpoints (type-routed, draft-only, never auto-sent)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.outreach import OutreachOut, OutreachRequest, OutreachUpdate
from app.services import outreach_service

router = APIRouter()


def _artifact_to_out(artifact) -> OutreachOut:
    d = outreach_service.to_out(artifact)
    return OutreachOut(
        id=d["id"],
        artifact_type=d["artifact_type"],
        subject=d.get("subject"),
        body=d["body"],
        rag_sources=[],
        status=d["status"],
        grounding=d.get("grounding", "unknown"),
    )


@router.post("/opportunities/{listing_id}/outreach", response_model=OutreachOut)
def generate_outreach(
    listing_id: uuid.UUID,
    payload: OutreachRequest,
    db: Session = Depends(get_db),
) -> OutreachOut:
    try:
        artifact = outreach_service.generate(db, listing_id, payload.user_id)
        return _artifact_to_out(artifact)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/outreach/{artifact_id}", response_model=OutreachOut)
def update_outreach(
    artifact_id: uuid.UUID,
    payload: OutreachUpdate,
    db: Session = Depends(get_db),
) -> OutreachOut:
    try:
        artifact = outreach_service.update(db, artifact_id, payload)
        return _artifact_to_out(artifact)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
