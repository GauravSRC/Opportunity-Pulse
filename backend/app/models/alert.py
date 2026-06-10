"""Alert / reminder model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import AlertChannel, AlertStatus


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("normalized_listings.id"), nullable=True, index=True
    )
    rule: Mapped[str] = mapped_column(String(128))
    channel: Mapped[AlertChannel] = mapped_column(ENUM(AlertChannel, name="alert_channel"))
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AlertStatus] = mapped_column(
        ENUM(AlertStatus, name="alert_status"), default=AlertStatus.pending
    )
