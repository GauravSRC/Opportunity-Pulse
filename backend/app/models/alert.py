"""Alert / reminder model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID
from app.models.enums import AlertChannel, AlertStatus


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("normalized_listings.id"), nullable=True, index=True
    )
    rule: Mapped[str] = mapped_column(String(128))
    channel: Mapped[AlertChannel] = mapped_column(Enum(AlertChannel, native_enum=False))
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False), default=AlertStatus.pending
    )
