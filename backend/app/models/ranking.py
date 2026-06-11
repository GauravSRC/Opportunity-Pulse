"""Per-user, per-listing rank scores with explainable components."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, json_type


class RankScore(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "rank_scores"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "listing_id", "model_version", name="uq_rank_user_listing_model"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("normalized_listings.id"), index=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0)
    # {"semantic": .., "skill_overlap": .., "recency": .., "urgency": .., "feedback": ..}
    components_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    matched_skills: Mapped[dict] = mapped_column(json_type(), default=list)
    model_version: Mapped[str] = mapped_column(String(64), default="v1")
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
