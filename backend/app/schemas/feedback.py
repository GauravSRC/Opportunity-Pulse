"""Feedback, alert, and source schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.enums import AccessMethod, AlertChannel, FeedbackSignal


class FeedbackIn(BaseModel):
    user_id: uuid.UUID
    listing_id: uuid.UUID
    signal: FeedbackSignal
    context: dict = {}


class AlertIn(BaseModel):
    rule: str
    channel: AlertChannel
    listing_id: uuid.UUID | None = None


class AlertUpdate(BaseModel):
    enabled: bool | None = None
    channel: AlertChannel | None = None


class SourceIn(BaseModel):
    key: str
    name: str
    category: str
    access_method: AccessMethod
    base_url: str | None = None
    config: dict = {}
    enabled: bool = True


class SourceUpdate(BaseModel):
    enabled: bool | None = None
    config: dict | None = None
