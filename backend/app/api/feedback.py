"""Feedback submission endpoint.

TODO(phase-6): persist feedback and enqueue the online weight-update job.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.common import Ack
from app.schemas.feedback import FeedbackIn

router = APIRouter()


@router.post("", response_model=Ack, status_code=202)
def submit_feedback(payload: FeedbackIn) -> Ack:
    raise HTTPException(status_code=501, detail="TODO(phase-6): submit_feedback")
