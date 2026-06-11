"""Offline demo fixture adapter.

Loads a bundled JSON file of diverse opportunities so the full pipeline
(normalize -> dedup -> deadline -> rank -> feed -> outreach) can be demoed and
tested with zero network access and no ToS concerns. Deterministic and
reproducible. Used by scripts/demo_seed.py and the integration tests.
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "sample_opportunities.json"


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


class DemoFixtureAdapter(SourceAdapter):
    key = "demo_fixture"
    access_method = AccessMethod.api
    category = "mixed"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        path = pathlib.Path(self.config.get("path") or _FIXTURE)
        records = json.loads(path.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        return [
            RawRecord(external_id=r["external_id"], url=r["url"], payload=r, fetched_at=now)
            for r in records
        ]

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        p = record.payload
        description = clean_text(p.get("description"))
        skills = p.get("skills") or extract_skills(description)
        return NormalizedListing(
            source_key=self.key,
            external_id=p["external_id"],
            title=p["title"],
            url=p["url"],
            type=p.get("type", "job"),
            org=p.get("org"),
            location=p.get("location"),
            is_remote=bool(p.get("is_remote")),
            posted_at=_parse_dt(p.get("posted_at")),
            description=description,
            skills=skills,
            links=p.get("links") or {},
            raw_text=description,
        )
