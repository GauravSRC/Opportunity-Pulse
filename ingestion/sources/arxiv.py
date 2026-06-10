"""arXiv adapter — surfaces research-active labs/authors.

Uses the arXiv API (Atom). Not job listings directly; feeds the research/lab
graph and outreach RAG (recent papers per author/institution). config:
{"categories": ["cs.LG", ...], "max_results": N}.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class ArxivAdapter(SourceAdapter):
    key = "arxiv"
    access_method = AccessMethod.api
    category = "research"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-1): query arXiv API; be polite (<=1 req/3s per their policy).
        raise NotImplementedError("ArxivAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        # TODO(phase-1): map paper -> research opportunity signal; type=research.
        raise NotImplementedError("ArxivAdapter.parse")
