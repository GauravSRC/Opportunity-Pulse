"""Embedding persistence helpers (portable across pgvector / SQLite JSON)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from agents.llm import get_embedder
from app.models.embedding import Embedding
from app.models.enums import EmbeddingOwner


def _as_floats(vector) -> list[float]:
    return [float(x) for x in (vector or [])]


def store_embedding(
    db: Session,
    owner_type: EmbeddingOwner,
    owner_id: uuid.UUID,
    vector: list[float],
    *,
    intent: str | None = None,
) -> None:
    """Replace any existing vector for (owner, intent) and store the new one."""
    db.execute(
        delete(Embedding).where(
            Embedding.owner_type == owner_type,
            Embedding.owner_id == owner_id,
            Embedding.intent == intent,
        )
    )
    emb = get_embedder()
    db.add(
        Embedding(
            owner_type=owner_type,
            owner_id=owner_id,
            intent=intent,
            model=emb.name,
            dim=emb.dim,
            vector=_as_floats(vector),
        )
    )


def get_embedding(
    db: Session, owner_type: EmbeddingOwner, owner_id: uuid.UUID, intent: str | None = None
) -> list[float] | None:
    row = db.execute(
        select(Embedding).where(
            Embedding.owner_type == owner_type,
            Embedding.owner_id == owner_id,
            Embedding.intent == intent,
        )
    ).scalar_one_or_none()
    return _as_floats(row.vector) if row else None


def get_listing_vectors(db: Session, listing_ids: list[uuid.UUID]) -> dict[str, list[float]]:
    if not listing_ids:
        return {}
    rows = db.execute(
        select(Embedding).where(
            Embedding.owner_type == EmbeddingOwner.listing,
            Embedding.owner_id.in_(listing_ids),
            Embedding.intent.is_(None),
        )
    ).scalars()
    return {str(r.owner_id): _as_floats(r.vector) for r in rows}
