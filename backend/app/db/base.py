"""SQLAlchemy declarative base + shared mixins.

Every model inherits ``id``, ``created_at``, ``updated_at`` via the mixins here.
Import all models in ``app.models`` so Alembic autogeneration sees them.
Column types come from ``app.db.types`` so models run on Postgres and SQLite.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.types import GUID


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
