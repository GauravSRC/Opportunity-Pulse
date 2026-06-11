"""Demo seed script.

Seeds a fresh database with:
  1. Sources from ingestion/registry.yaml
  2. Demo fixture opportunities (from ingestion/fixtures/sample_opportunities.json)
  3. A demo user + profile
  4. Rank scores for the demo user

Usage (from repo root, after `alembic upgrade head`):
    python scripts/demo_seed.py

Set DATABASE_URL in .env or environment before running.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure the monorepo packages are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def main() -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://opp:opp@localhost:5432/opportunitypulse",
    )

    engine = create_engine(database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()

    try:
        _seed(db)
    finally:
        db.close()
        engine.dispose()


def _seed(db) -> None:
    from app.services import pipeline, profile_service, ranking_service, source_service
    from sqlalchemy import select

    print("=== OpportunityPulse Demo Seed ===\n")

    # 1. Sync registry
    print("[1/5] Syncing source registry...")
    n = source_service.sync_registry(db)
    print(f"      {n} sources registered.\n")

    # 2. Ingest demo fixture
    print("[2/5] Ingesting demo fixture source...")
    from app.models.source import OpportunitySource
    source = db.execute(
        select(OpportunitySource).where(OpportunitySource.key == "demo_fixture")
    ).scalar_one_or_none()
    if source is None:
        print("      ERROR: demo_fixture source not found. Aborting.")
        return

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(pipeline.run_source(db, source, use_llm=False))
    loop.close()
    print(f"      created={result['created']} skipped={result['skipped']} errors={result['errors']}\n")

    # 3. Dedup
    print("[3/5] Running deduplication pass...")
    dedup_result = pipeline.dedup_all(db)
    print(f"      clusters={dedup_result['clusters']} listings={dedup_result['listings']}\n")

    # 4. Create demo user + profile
    print("[4/5] Creating demo user + profile...")

    class DemoProfile:
        email = "demo@opportunitypulse.dev"
        headline = "CS Student | ML & Backend"
        skills = [
            "Python", "Machine Learning", "PyTorch", "FastAPI",
            "SQL", "Git", "Docker", "React",
        ]
        intents = []
        locations = ["Remote", "San Francisco"]
        is_remote_ok = True
        education = {
            "degree": "B.Tech Computer Science",
            "institution": "IIT BHU",
            "graduation_year": 2025,
        }
        experience = {}
        preferences = {"min_stipend": 0, "max_commute_km": 50}

    profile = profile_service.create_profile(db, DemoProfile())
    print(f"      Profile id={profile.id}  user_id={profile.user_id}\n")

    # 5. Rank
    print("[5/5] Computing rank scores for demo user...")
    n_scored = ranking_service.rank_user(db, profile.user_id)
    print(f"      Scored {n_scored} opportunities.\n")

    # Show top 5
    items, total = ranking_service.get_feed(db, profile.user_id, limit=5)
    print(f"=== Top {len(items)} (of {total}) opportunities for demo user ===")
    for i, item in enumerate(items, 1):
        score_str = f"{item['score']:.3f}" if item["score"] is not None else "n/a"
        print(f"  {i}. [{score_str}] {item['title']} @ {item['org'] or '(unknown)'} [{item['type']}]")

    print("\nDone. Run `uvicorn app.main:app --reload` (from backend/) to explore the API.")


if __name__ == "__main__":
    main()
