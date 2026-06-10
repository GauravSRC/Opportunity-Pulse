"""Feedback signals feeding the learning loop."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import FeedbackSignal


class Feedback(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("normalized_listings.id"), index=True
    )
    signal: Mapped[FeedbackSignal] = mapped_column(ENUM(FeedbackSignal, name="feedback_signal"))
    weight: Mapped[float] = mapped_column(default=1.0)
    context_json: Mapped[dict] = mapped_column(JSONB, default=dict)
