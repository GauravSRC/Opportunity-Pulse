"""Outreach artifact model.

``artifact_type`` is chosen by the router from the opportunity type; a
``cold_email`` is produced ONLY for research/lab/professor opportunities.
Artifacts are never auto-sent: status moves draft -> approved/discarded by the
user only.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, json_type
from app.models.enums import ArtifactStatus, ArtifactType


class OutreachArtifact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "outreach_artifacts"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), index=True)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("normalized_listings.id"), index=True
    )
    artifact_type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType, native_enum=False))
    rag_sources_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[ArtifactStatus] = mapped_column(
        Enum(ArtifactStatus, native_enum=False), default=ArtifactStatus.draft
    )
    grounding: Mapped[str] = mapped_column(String(16), default="unknown")
    model_version: Mapped[str] = mapped_column(String(64), default="v1")
