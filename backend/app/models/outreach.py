"""Outreach artifact model.

``artifact_type`` is chosen by the router from the opportunity type; a
``cold_email`` is produced ONLY for research/lab/professor opportunities.
Artifacts are never auto-sent: status moves draft -> approved/discarded by the
user only.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ArtifactStatus, ArtifactType


class OutreachArtifact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "outreach_artifacts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("normalized_listings.id"), index=True
    )
    artifact_type: Mapped[ArtifactType] = mapped_column(ENUM(ArtifactType, name="artifact_type"))
    rag_sources_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[ArtifactStatus] = mapped_column(
        ENUM(ArtifactStatus, name="artifact_status"), default=ArtifactStatus.draft
    )
    model_version: Mapped[str] = mapped_column(String(64), default="v0")
