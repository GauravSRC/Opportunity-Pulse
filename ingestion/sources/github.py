"""GitHub adapter — OSS / GSoC discovery.

Uses the GitHub REST/Search API (auth via GITHUB_TOKEN) to find repos with
"good first issue" labels, GSoC org repos, and idea lists. config:
{"queries": [...], "labels": [...]}.
"""

from __future__ import annotations

from datetime import datetime

from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class GitHubAdapter(SourceAdapter):
    key = "github"
    access_method = AccessMethod.api
    category = "gsoc"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        # TODO(phase-1): authenticated search; respect GitHub rate limits.
        raise NotImplementedError("GitHubAdapter.fetch")

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        # TODO(phase-1): map repo/issue -> listing; type=gsoc or research.
        raise NotImplementedError("GitHubAdapter.parse")
