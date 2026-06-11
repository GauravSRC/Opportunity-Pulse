"""Pytest fixtures for the backend — uses SQLite in-memory for isolation."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Point to SQLite before the app boots so config picks it up
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("EMBEDDING_PROVIDER", "hashing")

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    # Import all models so their tables are registered
    import app.models  # noqa: F401
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    """Return a transactional test session rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestSession()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(engine):
    """TestClient with DB overridden to use the test SQLite engine."""
    connection = engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestSession()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()
