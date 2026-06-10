"""Per-user, per-listing rank scores with explainable components."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class RankScore(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "rank_scores"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", "model_version", name="uq_rank_user_listing_model"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("normalized_listings.id"), index=True
    )
    score: Mapped[float] = mapped_column(default=0.0)
    # {"semantic": .., "skill_overlap": .., "recency": .., "urgency": .., "feedback": ..}
    components_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    model_version: Mapped[str] = mapped_column(String(64), default="v0")
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
