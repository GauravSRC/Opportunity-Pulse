"""Regression tests for production issues.

Issue 1: rank_user crashed with "truth value of an array ... is ambiguous"
         because pgvector returns numpy arrays and the code truth-tested them.
Issue 2: demo_fixture listings leaked into the production feed; a purge endpoint
         removes a source's listings (and all dependent rows).
"""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

# ── helpers (mirror test_pipeline_integration) ────────────────────────────────


def _sync(db: Session) -> None:
    from app.services.source_service import sync_registry

    sync_registry(db)


def _ingest_demo(db: Session) -> dict:
    import asyncio

    from app.models.source import OpportunitySource
    from app.services.pipeline import run_source

    source = db.execute(
        select(OpportunitySource).where(OpportunitySource.key == "demo_fixture")
    ).scalar_one()
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(run_source(db, source))
    finally:
        loop.close()


def _create_profile(db: Session):
    from app.services.profile_service import create_profile

    class Payload:
        email = "fix@example.com"
        headline = "ML Engineer"
        skills = ["Python", "Machine Learning"]
        intents = []
        locations = ["Remote"]
        is_remote_ok = True
        education = {}
        experience = {}
        preferences = {}

    return create_profile(db, Payload())


# ── Issue 1: numpy truth-value regression ─────────────────────────────────────


class TestNumpyTruthValue:
    def test_as_floats_accepts_numpy_array(self) -> None:
        """pgvector hands back an ndarray; _as_floats must not truth-test it."""
        from app.services.embeddings import _as_floats

        arr = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        out = _as_floats(arr)  # would raise ValueError under `vector or []`
        assert out == pytest.approx([0.1, 0.2, 0.3], abs=1e-6)
        assert isinstance(out, list)

    def test_as_floats_none_and_list(self) -> None:
        from app.services.embeddings import _as_floats

        assert _as_floats(None) == []
        assert _as_floats([1, 2, 3]) == [1.0, 2.0, 3.0]

    def test_cosine_accepts_numpy_vectors(self) -> None:
        from ranking.retriever import cosine

        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert cosine(a, b) == pytest.approx(1.0)
        # length mismatch / empty must return 0.0, not raise
        assert cosine(np.array([1.0, 2.0]), np.array([1.0])) == 0.0
        assert cosine(np.array([]), np.array([])) == 0.0

    def test_rank_user_succeeds(self, db: Session) -> None:
        """End-to-end rank path (the crashing endpoint's core)."""
        from app.services.ranking_service import rank_user

        _sync(db)
        _ingest_demo(db)
        profile = _create_profile(db)
        n = rank_user(db, profile.user_id)
        assert n > 0

    def test_admin_rank_endpoint_succeeds(self, client: TestClient) -> None:
        """POST /admin/rank/{user_id} returns 200 (was 500: ValueError)."""
        client.post("/sources/sync")
        client.post("/sources/demo_fixture/ingest")
        prof = client.post(
            "/profiles",
            json={
                "email": "rank@example.com",
                "headline": "ML",
                "skills": ["Python"],
                "intents": [],
                "locations": ["Remote"],
                "is_remote_ok": True,
            },
        ).json()
        resp = client.post(f"/admin/rank/{prof['user_id']}")
        assert resp.status_code == 200, resp.text
        assert resp.json()["ok"] is True


# ── Issue 2: purge demo data ──────────────────────────────────────────────────


def _add_real_listing(db: Session):
    """Insert a non-demo source + listing + deadline + rank_score + embedding."""
    from datetime import UTC, datetime

    from app.models.deadline import Deadline
    from app.models.embedding import Embedding
    from app.models.enums import (
        AccessMethod,
        DeadlineKind,
        EmbeddingOwner,
        Extractor,
        OpportunityType,
    )
    from app.models.listing import NormalizedListing
    from app.models.ranking import RankScore
    from app.models.source import OpportunitySource
    from app.models.user import User

    real_src = OpportunitySource(
        key="remotive_real",
        name="Remotive",
        category="jobs",
        access_method=AccessMethod.api,
        enabled=True,
        health_json={},
    )
    db.add(real_src)
    db.flush()
    listing = NormalizedListing(
        source_id=real_src.id,
        title="Senior Python Engineer",
        org="RealCo",
        type=OpportunityType.job,
        url="https://remotive.com/jobs/123",
        is_remote=True,
        skills=["Python"],
        is_canonical=True,
    )
    db.add(listing)
    db.flush()
    db.add(Deadline(listing_id=listing.id, kind=DeadlineKind.unknown, confidence=0.0, extractor=Extractor.rule))
    db.add(Embedding(owner_type=EmbeddingOwner.listing, owner_id=listing.id, model="hashing", dim=3, vector=[0.1, 0.2, 0.3]))
    user = User(email="real@example.com", settings_json={})
    db.add(user)
    db.flush()
    db.add(
        RankScore(
            user_id=user.id,
            listing_id=listing.id,
            score=0.5,
            components_json={},
            matched_skills=[],
            model_version="v1",
            computed_at=datetime.now(UTC),
        )
    )
    db.commit()
    return real_src, listing


class TestPurgeSource:
    def test_purge_removes_demo_keeps_real(self, db: Session) -> None:
        from app.models.deadline import Deadline
        from app.models.embedding import Embedding
        from app.models.listing import NormalizedListing, RawListing
        from app.models.ranking import RankScore
        from app.services.ranking_service import rank_user
        from app.services.source_service import get_source, purge_source

        _sync(db)
        _ingest_demo(db)
        profile = _create_profile(db)
        rank_user(db, profile.user_id)  # creates rank_scores for demo listings

        real_src, real_listing = _add_real_listing(db)
        demo = get_source(db, "demo_fixture")
        demo_count = db.execute(
            select(NormalizedListing).where(NormalizedListing.source_id == demo.id)
        ).scalars().all()
        assert len(demo_count) > 0

        result = purge_source(db, "demo_fixture")

        assert result["deleted"]["listings"] == len(demo_count)
        assert result["disabled"] is True
        # demo source disabled, demo listings + dependents gone
        assert get_source(db, "demo_fixture").enabled is False
        assert (
            db.execute(select(NormalizedListing).where(NormalizedListing.source_id == demo.id))
            .scalars()
            .first()
            is None
        )
        assert db.execute(select(RawListing).where(RawListing.source_id == demo.id)).scalars().first() is None
        # real source untouched
        assert db.get(NormalizedListing, real_listing.id) is not None
        assert db.execute(select(Deadline).where(Deadline.listing_id == real_listing.id)).scalars().first() is not None
        assert db.execute(select(RankScore).where(RankScore.listing_id == real_listing.id)).scalars().first() is not None
        assert db.execute(select(Embedding).where(Embedding.owner_id == real_listing.id)).scalars().first() is not None

    def test_purge_unknown_source_returns_none(self, db: Session) -> None:
        from app.services.source_service import purge_source

        assert purge_source(db, "does_not_exist") is None

    def test_purge_endpoint_clears_feed(self, client: TestClient) -> None:
        client.post("/sources/sync")
        client.post("/sources/demo_fixture/ingest")
        before = client.get("/opportunities").json()
        assert before["total"] > 0

        resp = client.post("/admin/sources/demo_fixture/purge")
        assert resp.status_code == 200, resp.text

        after = client.get("/opportunities").json()
        assert after["total"] == 0
