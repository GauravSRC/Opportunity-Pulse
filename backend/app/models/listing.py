"""Raw + normalized listings and dedup clusters."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import OpportunityType, RawStatus


class RawListing(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "raw_listings"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunity_sources.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    url: Mapped[str] = mapped_column(String(1024))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    content_fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[RawStatus] = mapped_column(
        ENUM(RawStatus, name="raw_status"), default=RawStatus.new
    )


class DedupCluster(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dedup_clusters"

    canonical_listing_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    member_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)
    method_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    confidence: Mapped[float] = mapped_column(default=0.0)
    merged_metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class NormalizedListing(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "normalized_listings"

    raw_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("raw_listings.id"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunity_sources.id"), index=True)
    title: Mapped[str] = mapped_column(String(512))
    org: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[OpportunityType] = mapped_column(ENUM(OpportunityType, name="opportunity_type"))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    url: Mapped[str] = mapped_column(String(1024))
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    links_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("dedup_clusters.id"), nullable=True, index=True
    )
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True)
