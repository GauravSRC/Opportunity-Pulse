"""Audit log for sensitive actions (data access, source changes, sends)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin
from app.db.types import GUID, json_type


class AuditLog(UUIDMixin, Base):
    __tablename__ = "audit_logs"

    actor: Mapped[str] = mapped_column(String(128))  # user id or "system:<agent>"
    action: Mapped[str] = mapped_column(String(128))
    entity: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    meta_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
