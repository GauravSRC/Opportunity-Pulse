"""Generic RSS/Atom adapter — reused for any feed-providing source.

config: {"feed_url": "...", "type": "fellowship"|"conference"|..., "org": "..."}.
Preferred rung above scraping for fellowship/CFP/lab-news feeds.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ingestion.normalize import clean_text, extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class RssGenericAdapter(SourceAdapter):
    key = "rss_generic"
    access_method = AccessMethod.rss
    category = "mixed"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        import feedparser  # lazy

        feed_url = self.config["feed_url"]
        parsed = feedparser.parse(feed_url)
        now = datetime.now(timezone.utc)
        records = []
        for e in parsed.entries:
            ext = e.get("id") or e.get("link") or e.get("title", "")
            records.append(
                RawRecord(external_id=str(ext), url=e.get("link", ""), payload=dict(e), fetched_at=now)
            )
        return records

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        e = record.payload
        title = e.get("title")
        if not title:
            return None
        description = clean_text(e.get("summary") or e.get("description"))
        posted = None
        if e.get("published_parsed"):
            try:
                posted = datetime(*e["published_parsed"][:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                posted = None
        return NormalizedListing(
            source_key=self.config.get("source_key", self.key),
            external_id=str(record.external_id),
            title=title,
            url=e.get("link", ""),
            type=self.config.get("type", "job"),
            org=self.config.get("org"),
            location=self.config.get("location"),
            is_remote=bool(self.config.get("is_remote", False)),
            posted_at=posted,
            description=description,
            skills=extract_skills(f"{title} {description}"),
            links={"apply_url": e.get("link", "")},
            raw_text=description,
        )
