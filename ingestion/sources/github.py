"""GitHub adapter — OSS / GSoC discovery via the Search API.

Uses GITHUB_TOKEN. config: {"queries": ["label:\"good first issue\" ..."]}.
Each matching issue becomes a gsoc/research-flavored opportunity.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_SEARCH = "https://api.github.com/search/issues"


class GitHubAdapter(SourceAdapter):
    key = "github"
    access_method = AccessMethod.api
    category = "gsoc"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        s = get_settings()
        headers = {"User-Agent": s.crawler_user_agent, "Accept": "application/vnd.github+json"}
        if s.github_token:
            headers["Authorization"] = f"Bearer {s.github_token}"
        now = datetime.now(timezone.utc)
        records: list[RawRecord] = []
        async with httpx.AsyncClient(timeout=s.http_timeout_seconds, headers=headers) as client:
            for q in self.config.get("queries", []):
                resp = await client.get(_SEARCH, params={"q": q, "per_page": 25})
                resp.raise_for_status()
                for item in resp.json().get("items", []):
                    records.append(
                        RawRecord(
                            external_id=str(item["id"]),
                            url=item.get("html_url", ""),
                            payload=item,
                            fetched_at=now,
                        )
                    )
        return records

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        it = record.payload
        if not it.get("title"):
            return None
        description = clean_text(it.get("body"))
        posted = None
        if it.get("created_at"):
            try:
                posted = datetime.fromisoformat(it["created_at"].replace("Z", "+00:00"))
            except ValueError:
                posted = None
        repo = (it.get("repository_url") or "").rsplit("/", 1)[-1] or None
        return NormalizedListing(
            source_key=self.key,
            external_id=str(it["id"]),
            title=it["title"],
            url=it.get("html_url", ""),
            type="gsoc",
            org=repo,
            location="Remote",
            is_remote=True,
            posted_at=posted,
            description=description,
            skills=extract_skills(f"{it['title']} {description}"),
            links={"apply_url": it.get("html_url", "")},
            raw_text=description,
        )
