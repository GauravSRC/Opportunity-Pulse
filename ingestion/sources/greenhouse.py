"""Greenhouse ATS adapter (JSON job board API).

Endpoint pattern: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs
Structured + ToS-friendly; no scraping needed. config: {"slug": "<company>"}.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class GreenhouseAdapter(SourceAdapter):
    key = "greenhouse"
    access_method = AccessMethod.ats_json
    category = "jobs"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-1): GET board jobs for self.config["slug"] via httpx.
        raise NotImplementedError("GreenhouseAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        # TODO(phase-1): map title/location/url/content; type=job.
        raise NotImplementedError("GreenhouseAdapter.parse")
