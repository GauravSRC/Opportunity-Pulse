"""Polymorphic embedding store.

One row per (owner_type, owner_id, intent?) vector. Profiles may have several
rows (one per intent) for intent-aware retrieval. Vectors use pgvector on
Postgres (HNSW cosine index added in the migration) and a JSON list on SQLite.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import DEFAULT_EMBEDDING_DIM, GUID, vector_type
from app.models.enums import EmbeddingOwner


class Embedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "embeddings"

    owner_type: Mapped[EmbeddingOwner] = mapped_column(
        Enum(EmbeddingOwner, native_enum=False), index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str] = mapped_column(String(128))
    dim: Mapped[int] = mapped_column(Integer, default=DEFAULT_EMBEDDING_DIM)
    vector: Mapped[list[float]] = mapped_column(vector_type(DEFAULT_EMBEDDING_DIM))
