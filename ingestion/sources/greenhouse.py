"""Greenhouse ATS adapter (JSON job board API).

Endpoint: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
Structured + ToS-friendly; no scraping. config: {"slug": "<company>"}.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
from app.core.config import get_settings

from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_BASE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


class GreenhouseAdapter(SourceAdapter):
    key = "greenhouse"
    access_method = AccessMethod.ats_json
    category = "jobs"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        slug = self.config["slug"]
        s = get_settings()
        async with httpx.AsyncClient(
            timeout=s.http_timeout_seconds, headers={"User-Agent": s.crawler_user_agent}
        ) as client:
            resp = await client.get(_BASE.format(slug=slug))
            resp.raise_for_status()
            jobs = resp.json().get("jobs", [])
        now = datetime.now(UTC)
        return [
            RawRecord(external_id=str(j["id"]), url=j.get("absolute_url", ""), payload=j, fetched_at=now)
            for j in jobs
        ]

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        j = record.payload
        if not j.get("title"):
            return None
        description = clean_text(j.get("content"))
        posted = None
        if j.get("updated_at"):
            try:
                posted = datetime.fromisoformat(j["updated_at"].replace("Z", "+00:00"))
            except ValueError:
                posted = None
        return NormalizedListing(
            source_key=self.key,
            external_id=str(j["id"]),
            title=j["title"],
            url=j.get("absolute_url", ""),
            type="internship" if "intern" in j["title"].lower() else "job",
            org=(self.config.get("company") or self.config.get("slug")),
            location=(j.get("location") or {}).get("name"),
            is_remote="remote" in ((j.get("location") or {}).get("name", "")).lower(),
            posted_at=posted,
            description=description,
            skills=extract_skills(description),
            links={"apply_url": j.get("absolute_url", "")},
            raw_text=description,
        )
