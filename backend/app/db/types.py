"""Database-portable column types.

Production runs on PostgreSQL + pgvector; tests and quick local runs use SQLite.
These helpers keep one model definition working on both: native Postgres types
(UUID, JSONB, ARRAY, pgvector) where available, JSON-encoded fallbacks on SQLite.

Vectors are stored in pgvector on Postgres (with the HNSW index from the initial
migration) and as a JSON list on SQLite. Retrieval computes cosine in Python at
MVP scale, so behaviour is identical across backends — the pgvector index is a
production performance optimization, not a correctness dependency.
"""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import CHAR, JSON, String, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Default embedding dimensionality (BAAI/bge-small-en-v1.5 and the hashing
# fallback both emit 384-d vectors).
DEFAULT_EMBEDDING_DIM = 384


class GUID(TypeDecorator):
    """UUID on Postgres, 32-char hex string on other backends."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        return value if dialect.name == "postgresql" else value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


def json_type():
    """JSONB on Postgres, JSON elsewhere."""
    return JSON().with_variant(JSONB(), "postgresql")


def str_array():
    """text[] on Postgres, JSON list elsewhere."""
    return JSON().with_variant(ARRAY(String()), "postgresql")


def uuid_array():
    """uuid[] on Postgres, JSON list elsewhere."""
    return JSON().with_variant(ARRAY(PG_UUID(as_uuid=True)), "postgresql")


def vector_type(dim: int = DEFAULT_EMBEDDING_DIM):
    """pgvector Vector on Postgres, JSON list elsewhere."""
    return JSON().with_variant(Vector(dim), "postgresql")
