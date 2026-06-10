"""Lever ATS adapter (JSON postings API).

Endpoint pattern: https://api.lever.co/v0/postings/{company}?mode=json
config: {"company": "<slug>"}.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class LeverAdapter(SourceAdapter):
    key = "lever"
    access_method = AccessMethod.ats_json
    category = "jobs"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        raise NotImplementedError("LeverAdapter.fetch")  # TODO(phase-1)

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        raise NotImplementedError("LeverAdapter.parse")  # TODO(phase-1)
