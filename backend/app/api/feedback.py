"""Feedback submission endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import Ack
from app.schemas.feedback import FeedbackIn
from app.services import feedback_service

router = APIRouter()


@router.post("", response_model=Ack, status_code=202)
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)) -> Ack:
    try:
        feedback_service.submit(db, payload)
        return Ack(ok=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
