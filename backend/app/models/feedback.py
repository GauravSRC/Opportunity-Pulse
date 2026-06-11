"""Feedback signals feeding the learning loop."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, json_type
from app.models.enums import FeedbackSignal


class Feedback(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("normalized_listings.id"), index=True
    )
    signal: Mapped[FeedbackSignal] = mapped_column(Enum(FeedbackSignal, native_enum=False))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    context_json: Mapped[dict] = mapped_column(json_type(), default=dict)
