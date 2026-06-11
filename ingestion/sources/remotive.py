"""Remotive adapter (public remote-jobs JSON API).

Endpoint: https://remotive.com/api/remote-jobs?limit=N&category=...
Free, structured, remote-only listings. config: {"limit": N, "category": "..."}.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_BASE = "https://remotive.com/api/remote-jobs"


class RemotiveAdapter(SourceAdapter):
    key = "remotive"
    access_method = AccessMethod.api
    category = "jobs"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        s = get_settings()
        params = {"limit": self.config.get("limit", 50)}
        if self.config.get("category"):
            params["category"] = self.config["category"]
        async with httpx.AsyncClient(
            timeout=s.http_timeout_seconds, headers={"User-Agent": s.crawler_user_agent}
        ) as client:
            resp = await client.get(_BASE, params=params)
            resp.raise_for_status()
            jobs = resp.json().get("jobs", [])
        now = datetime.now(timezone.utc)
        return [
            RawRecord(external_id=str(j["id"]), url=j.get("url", ""), payload=j, fetched_at=now)
            for j in jobs
        ]

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        j = record.payload
        if not j.get("title"):
            return None
        description = clean_text(j.get("description"))
        posted = None
        if j.get("publication_date"):
            try:
                posted = datetime.fromisoformat(j["publication_date"]).replace(tzinfo=timezone.utc)
            except ValueError:
                posted = None
        return NormalizedListing(
            source_key=self.key,
            external_id=str(j["id"]),
            title=j["title"],
            url=j.get("url", ""),
            type="internship" if "intern" in j["title"].lower() else "job",
            org=j.get("company_name"),
            location=j.get("candidate_required_location") or "Remote",
            is_remote=True,
            posted_at=posted,
            description=description,
            skills=extract_skills(f"{j.get('title','')} {description}"),
            links={"apply_url": j.get("url", "")},
            raw_text=description,
        )
