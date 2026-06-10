"""Web-discovery adapter via the search provider (Tavily default / SerpAPI).

Last structured rung before headless scraping: expands profile intents into
queries, finds candidate listing URLs, then hands them to per-domain parsing.
config: {"queries": [...], "type": "..."}. Honors robots.txt before fetching
any discovered page.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class TavilySearchAdapter(SourceAdapter):
    key = "search_tavily"
    access_method = AccessMethod.search
    category = "mixed"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-2): call the configured search provider; dedupe URLs.
        raise NotImplementedError("TavilySearchAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        # TODO(phase-2): extract main content (readability) -> listing.
        raise NotImplementedError("TavilySearchAdapter.parse")
