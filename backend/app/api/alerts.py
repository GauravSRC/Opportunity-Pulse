"""Alert subscription endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.models.enums import AlertChannel, AlertStatus
from app.schemas.feedback import AlertIn, AlertUpdate

router = APIRouter()


def _alert_out(a: Alert) -> dict:
    return {
        "id": a.id,
        "user_id": a.user_id,
        "listing_id": a.listing_id,
        "rule": a.rule,
        "channel": a.channel.value,
        "status": a.status.value,
        "scheduled_for": a.scheduled_for,
        "sent_at": a.sent_at,
    }


@router.get("")
def list_alerts(user_id: uuid.UUID, db: Session = Depends(get_db)) -> list[dict]:
    alerts = db.execute(
        select(Alert).where(Alert.user_id == user_id)
    ).scalars().all()
    return [_alert_out(a) for a in alerts]


@router.post("", status_code=201)
def create_alert(payload: AlertIn, user_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    alert = Alert(
        user_id=user_id,
        listing_id=payload.listing_id,
        rule=payload.rule,
        channel=AlertChannel(payload.channel.value),
        status=AlertStatus.pending,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return _alert_out(alert)


@router.patch("/{alert_id}")
def update_alert(
    alert_id: uuid.UUID,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
) -> dict:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if payload.channel is not None:
        alert.channel = AlertChannel(payload.channel.value)
    db.commit()
    db.refresh(alert)
    return _alert_out(alert)
