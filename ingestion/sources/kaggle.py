"""Kaggle adapter — competitions as hackathon-like opportunities.

Uses the Kaggle API (KAGGLE_USERNAME / KAGGLE_KEY). Also a source of offline
evaluation datasets. config: {"category": "featured"|"research"|...}.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class KaggleAdapter(SourceAdapter):
    key = "kaggle"
    access_method = AccessMethod.api
    category = "hackathon"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-1): list competitions; deadline = competition end date.
        raise NotImplementedError("KaggleAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        raise NotImplementedError("KaggleAdapter.parse")  # TODO(phase-1)
