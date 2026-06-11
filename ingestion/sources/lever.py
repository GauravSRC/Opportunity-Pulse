"""Lever ATS adapter (JSON postings API).

Endpoint: https://api.lever.co/v0/postings/{company}?mode=json
config: {"company": "<slug>"}.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
from app.core.config import get_settings

from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_BASE = "https://api.lever.co/v0/postings/{company}?mode=json"


class LeverAdapter(SourceAdapter):
    key = "lever"
    access_method = AccessMethod.ats_json
    category = "jobs"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        company = self.config["company"]
        s = get_settings()
        async with httpx.AsyncClient(
            timeout=s.http_timeout_seconds, headers={"User-Agent": s.crawler_user_agent}
        ) as client:
            resp = await client.get(_BASE.format(company=company))
            resp.raise_for_status()
            postings = resp.json()
        now = datetime.now(UTC)
        return [
            RawRecord(external_id=str(p["id"]), url=p.get("hostedUrl", ""), payload=p, fetched_at=now)
            for p in postings
        ]

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        p = record.payload
        if not p.get("text"):
            return None
        description = clean_text(p.get("descriptionPlain") or p.get("description"))
        posted = None
        if p.get("createdAt"):
            try:
                posted = datetime.fromtimestamp(int(p["createdAt"]) / 1000, tz=UTC)
            except (ValueError, TypeError):
                posted = None
        location = (p.get("categories") or {}).get("location")
        return NormalizedListing(
            source_key=self.key,
            external_id=str(p["id"]),
            title=p["text"],
            url=p.get("hostedUrl", ""),
            type="internship" if "intern" in p["text"].lower() else "job",
            org=self.config.get("company"),
            location=location,
            is_remote="remote" in (location or "").lower(),
            posted_at=posted,
            description=description,
            skills=extract_skills(description),
            links={"apply_url": p.get("applyUrl") or p.get("hostedUrl", "")},
            raw_text=description,
        )
