"""Alert subscription endpoints.

TODO(phase-3): CRUD alert rules; the notification flow dispatches them.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.schemas.feedback import AlertIn, AlertUpdate

router = APIRouter()


@router.get("")
def list_alerts() -> list[dict]:
    raise HTTPException(status_code=501, detail="TODO(phase-3): list_alerts")


@router.post("", status_code=201)
def create_alert(payload: AlertIn) -> dict:
    raise HTTPException(status_code=501, detail="TODO(phase-3): create_alert")


@router.patch("/{alert_id}")
def update_alert(alert_id: uuid.UUID, payload: AlertUpdate) -> dict:
    raise HTTPException(status_code=501, detail="TODO(phase-3): update_alert")
