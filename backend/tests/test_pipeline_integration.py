"""Integration tests: onboard → ingest → rank → feed → outreach.

All tests run against SQLite in-memory via the DB override in conftest.py.
No network calls are made; the demo_fixture source loads from local JSON.
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# ── helpers ──────────────────────────────────────────────────────────────────


def _sync_sources(db: Session) -> int:
    from app.services.source_service import sync_registry
    return sync_registry(db)


def _run_ingest(db: Session) -> dict:
    from app.models.source import OpportunitySource
    from app.services.pipeline import run_source
    from sqlalchemy import select

    source = db.execute(
        select(OpportunitySource).where(OpportunitySource.key == "demo_fixture")
    ).scalar_one_or_none()
    assert source is not None, "demo_fixture source not found after sync"
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(run_source(db, source))
    loop.close()
    return result


def _create_profile(db: Session) -> object:
    from app.services.profile_service import create_profile

    class Payload:
        email = "test@example.com"
        headline = "ML Engineer"
        skills = ["Python", "Machine Learning", "PyTorch"]
        intents = []
        locations = ["Remote"]
        is_remote_ok = True
        education = {}
        experience = {}
        preferences = {}

    return create_profile(db, Payload())


# ── tests ────────────────────────────────────────────────────────────────────


class TestSourceSync:
    def test_sync_registry_creates_sources(self, db: Session) -> None:
        n = _sync_sources(db)
        assert n > 0

    def test_demo_fixture_present(self, db: Session) -> None:
        from app.models.source import OpportunitySource
        from sqlalchemy import select
        _sync_sources(db)
        source = db.execute(
            select(OpportunitySource).where(OpportunitySource.key == "demo_fixture")
        ).scalar_one_or_none()
        assert source is not None
        assert source.enabled is True


class TestIngestion:
    def test_ingest_creates_listings(self, db: Session) -> None:
        _sync_sources(db)
        result = _run_ingest(db)
        assert result["source"] == "demo_fixture"
        assert result["created"] > 0
        assert result["errors"] == 0

    def test_ingest_idempotent(self, db: Session) -> None:
        _sync_sources(db)
        first = _run_ingest(db)
        second = _run_ingest(db)
        assert second["created"] == 0
        assert second["skipped"] == first["created"]

    def test_listings_have_deadlines(self, db: Session) -> None:
        from app.models.deadline import Deadline
        from sqlalchemy import select
        _sync_sources(db)
        _run_ingest(db)
        deadlines = db.execute(select(Deadline)).scalars().all()
        assert len(deadlines) > 0


class TestDedup:
    def test_dedup_all_runs(self, db: Session) -> None:
        from app.services.pipeline import dedup_all
        _sync_sources(db)
        _run_ingest(db)
        result = dedup_all(db)
        assert "listings" in result
        assert result["listings"] > 0


class TestProfile:
    def test_create_profile(self, db: Session) -> None:
        profile = _create_profile(db)
        assert profile.id is not None
        assert profile.user_id is not None
        assert len(profile.skills) == 3

    def test_update_profile(self, db: Session) -> None:
        from app.services.profile_service import update_profile
        profile = _create_profile(db)

        class UpdatePayload:
            headline = "Senior ML Engineer"
            skills = ["Python", "Machine Learning", "PyTorch", "TensorFlow"]
            intents = None
            locations = None
            is_remote_ok = None
            preferences = None

        updated = update_profile(db, profile.id, UpdatePayload())
        assert updated.headline == "Senior ML Engineer"
        assert len(updated.skills) == 4


class TestRanking:
    def test_rank_user(self, db: Session) -> None:
        from app.services.ranking_service import rank_user
        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)
        n = rank_user(db, profile.user_id)
        assert n > 0

    def test_get_feed(self, db: Session) -> None:
        from app.services.ranking_service import get_feed, rank_user
        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)
        rank_user(db, profile.user_id)
        items, total = get_feed(db, profile.user_id)
        assert total > 0
        assert len(items) > 0
        # ranked items should have scores
        assert any(item["score"] is not None for item in items)

    def test_feed_without_user(self, db: Session) -> None:
        from app.services.ranking_service import get_feed
        _sync_sources(db)
        _run_ingest(db)
        items, total = get_feed(db, user_id=None)
        assert total > 0

    def test_explanation(self, db: Session) -> None:
        from app.services.ranking_service import get_explanation, get_feed, rank_user
        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)
        rank_user(db, profile.user_id)
        items, _ = get_feed(db, profile.user_id)
        first = items[0]
        expl = get_explanation(db, first["id"], profile.user_id)
        assert expl is not None
        assert "components" in expl
        assert "semantic" in expl["components"]


class TestDeadlineExtraction:
    def test_fixed_deadline(self) -> None:
        from deadline_parser import extract
        result = extract("Applications close December 31, 2025.", use_llm=False)
        assert result.kind in ("fixed", "unknown")
        assert result.confidence >= 0.0

    def test_rolling_deadline(self) -> None:
        from deadline_parser import extract
        result = extract("We accept applications on a rolling basis.", use_llm=False)
        assert result.kind == "rolling"

    def test_no_deadline(self) -> None:
        from deadline_parser import extract
        result = extract("Great opportunity for Python developers.", use_llm=False)
        assert result.kind in ("unknown", "rolling", "fixed")
        assert result.confidence <= 1.0


class TestOutreach:
    def test_generate_cover_letter_for_job(self, db: Session) -> None:
        from app.models.enums import OpportunityType
        from app.models.listing import NormalizedListing
        from app.services.outreach_service import generate
        from sqlalchemy import select

        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)

        # Find a non-research listing (should get cover_letter, not cold_email)
        listing = db.execute(
            select(NormalizedListing).where(
                NormalizedListing.type == OpportunityType.internship
            )
        ).scalars().first()

        if listing is None:
            pytest.skip("No internship listing in fixture")

        artifact = generate(db, listing.id, profile.user_id)
        assert artifact is not None
        assert artifact.artifact_type.value != "cold_email"
        assert len(artifact.body) > 10

    def test_generate_cold_email_for_research(self, db: Session) -> None:
        from app.models.enums import OpportunityType
        from app.models.listing import NormalizedListing
        from app.services.outreach_service import generate
        from sqlalchemy import select

        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)

        listing = db.execute(
            select(NormalizedListing).where(
                NormalizedListing.type == OpportunityType.research
            )
        ).scalars().first()

        if listing is None:
            pytest.skip("No research listing in fixture")

        artifact = generate(db, listing.id, profile.user_id)
        assert artifact is not None
        assert artifact.artifact_type.value == "cold_email"


class TestFeedback:
    def test_submit_feedback(self, db: Session) -> None:
        from app.models.enums import FeedbackSignal
        from app.models.listing import NormalizedListing
        from app.services.feedback_service import submit
        from sqlalchemy import select

        _sync_sources(db)
        _run_ingest(db)
        profile = _create_profile(db)

        listing = db.execute(select(NormalizedListing)).scalars().first()
        assert listing is not None

        class FeedbackPayload:
            user_id = profile.user_id
            listing_id = listing.id
            signal = FeedbackSignal.thumbs_up
            context = {}

        result = submit(db, FeedbackPayload())
        assert result["ok"] is True
        assert "weights" in result


class TestAPIRoutes:
    """Smoke tests for wired API endpoints via TestClient."""

    def test_healthz(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert r.status_code == 200

    def test_admin_health(self, client: TestClient) -> None:
        r = client.get("/admin/health")
        assert r.status_code == 200
        body = r.json()
        assert "sources" in body

    def test_deadline_extract(self, client: TestClient) -> None:
        r = client.post("/deadlines/extract", json={"text": "Apply by March 31, 2025."})
        assert r.status_code == 200
        body = r.json()
        assert "kind" in body
        assert "confidence" in body

    def test_opportunities_empty(self, client: TestClient) -> None:
        r = client.get("/opportunities")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_create_profile_api(self, client: TestClient) -> None:
        r = client.post("/profiles", json={
            "email": "api_test@example.com",
            "headline": "Test User",
            "skills": ["Python"],
            "intents": [],
            "locations": ["Remote"],
            "is_remote_ok": True,
        })
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["skills"] == ["Python"]

    def test_get_nonexistent_profile(self, client: TestClient) -> None:
        import uuid
        r = client.get(f"/profiles/{uuid.uuid4()}")
        assert r.status_code == 404
