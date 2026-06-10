"""Polymorphic embedding store (pgvector).

One row per (owner_type, owner_id, intent?) vector. Profiles may have several
rows (one per intent) for intent-aware retrieval. An HNSW cosine index is added
in the migration.
"""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import EmbeddingOwner

# Default embedding dimensionality (BAAI/bge-small-en-v1.5 -> 384).
DEFAULT_EMBEDDING_DIM = 384


class Embedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "embeddings"

    owner_type: Mapped[EmbeddingOwner] = mapped_column(
        ENUM(EmbeddingOwner, name="embedding_owner"), index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str] = mapped_column(String(128))
    dim: Mapped[int] = mapped_column(Integer, default=DEFAULT_EMBEDDING_DIM)
    vector: Mapped[list[float]] = mapped_column(Vector(DEFAULT_EMBEDDING_DIM))
