"""arXiv adapter — surfaces research-active labs/authors.

Uses the arXiv Atom API. Feeds the research graph and outreach RAG (recent
papers per category/author). config: {"categories": ["cs.LG"], "max_results": N}.
Polite: arXiv asks for <= 1 request / 3s.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter

_BASE = "http://export.arxiv.org/api/query"


class ArxivAdapter(SourceAdapter):
    key = "arxiv"
    access_method = AccessMethod.api
    category = "research"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        import feedparser  # lazy

        s = get_settings()
        cats = " OR ".join(f"cat:{c}" for c in self.config.get("categories", ["cs.LG"]))
        params = {
            "search_query": cats,
            "start": 0,
            "max_results": self.config.get("max_results", 25),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        async with httpx.AsyncClient(
            timeout=s.http_timeout_seconds, headers={"User-Agent": s.crawler_user_agent}
        ) as client:
            resp = await client.get(_BASE, params=params)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        now = datetime.now(timezone.utc)
        return [
            RawRecord(external_id=e.get("id", ""), url=e.get("link", ""), payload=dict(e), fetched_at=now)
            for e in feed.entries
        ]

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        e = record.payload
        if not e.get("title"):
            return None
        description = clean_text(e.get("summary"))
        authors = ", ".join(a.get("name", "") for a in e.get("authors", []))[:240]
        posted = None
        if e.get("published_parsed"):
            try:
                posted = datetime(*e["published_parsed"][:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                posted = None
        return NormalizedListing(
            source_key=self.key,
            external_id=str(e.get("id", "")),
            title=e["title"].replace("\n", " ").strip(),
            url=e.get("link", ""),
            type="research",
            org=authors or "arXiv",
            location="Remote",
            is_remote=True,
            posted_at=posted,
            description=description,
            skills=extract_skills(f"{e['title']} {description}"),
            links={"paper_urls": [e.get("link", "")]},
            raw_text=description,
        )
