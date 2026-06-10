"""Generic RSS/Atom adapter — reused for any feed-providing source.

config: {"feed_url": "...", "type": "fellowship"|"conference"|...}. This is the
preferred rung above scraping for many fellowship/CFP/lab-news sources.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class RssGenericAdapter(SourceAdapter):
    key = "rss_generic"
    access_method = AccessMethod.rss
    category = "mixed"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-1): feedparser.parse(config["feed_url"]); conditional GET.
        raise NotImplementedError("RssGenericAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        # TODO(phase-1): map entry title/link/summary; type from config.
        raise NotImplementedError("RssGenericAdapter.parse")
