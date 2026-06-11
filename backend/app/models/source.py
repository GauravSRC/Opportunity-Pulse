"""Opportunity source registry model.

Mirrors the static ``ingestion/registry.yaml`` but tracks runtime state
(enabled flag, health metrics, last run). The source-health monitor updates
``health_json`` and may flip ``enabled`` to false on repeated failures.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import json_type
from app.models.enums import AccessMethod


class OpportunitySource(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "opportunity_sources"

    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64))
    access_method: Mapped[AccessMethod] = mapped_column(Enum(AccessMethod, native_enum=False))
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    config_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    health_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
