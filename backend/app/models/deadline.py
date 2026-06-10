"""Deadline model — output of the extraction fallback ladder."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import DeadlineKind, Extractor


class Deadline(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "deadlines"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("normalized_listings.id"), index=True
    )
    kind: Mapped[DeadlineKind] = mapped_column(ENUM(DeadlineKind, name="deadline_kind"))
    resolved_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    anchor_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_phrase: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(default=0.0)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    extractor: Mapped[Extractor] = mapped_column(ENUM(Extractor, name="extractor"))
