"""Kaggle adapter — competitions as hackathon-like opportunities.

Uses the Kaggle API (KAGGLE_USERNAME / KAGGLE_KEY via the kaggle package).
config: {"category": "featured"}. The competition deadline becomes the listing
deadline phrase so the extractor can pick it up.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ingestion.normalize import extract_skills
from ingestion.sources.base import AccessMethod, NormalizedListing, RawRecord, SourceAdapter


class KaggleAdapter(SourceAdapter):
    key = "kaggle"
    access_method = AccessMethod.api
    category = "hackathon"

    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        from kaggle.api.kaggle_api_extended import KaggleApi  # lazy; needs creds

        api = KaggleApi()
        api.authenticate()
        comps = api.competitions_list(category=self.config.get("category", "featured"))
        now = datetime.now(UTC)
        records = []
        for c in comps:
            payload = {
                "ref": getattr(c, "ref", ""),
                "title": getattr(c, "title", ""),
                "description": getattr(c, "description", ""),
                "deadline": str(getattr(c, "deadline", "")),
                "url": f"https://www.kaggle.com/competitions/{getattr(c, 'ref', '')}",
            }
            records.append(
                RawRecord(external_id=payload["ref"], url=payload["url"], payload=payload, fetched_at=now)
            )
        return records

    def parse(self, record: RawRecord) -> NormalizedListing | None:
        p = record.payload
        if not p.get("title"):
            return None
        deadline = p.get("deadline")
        description = f"{p.get('description', '')} Competition deadline: {deadline}." if deadline else p.get("description", "")
        return NormalizedListing(
            source_key=self.key,
            external_id=str(p["ref"]),
            title=p["title"],
            url=p["url"],
            type="hackathon",
            org="Kaggle",
            location="Remote",
            is_remote=True,
            posted_at=None,
            description=description,
            skills=extract_skills(f"{p['title']} {description}") or ["Data Science", "Machine Learning"],
            links={"event_page": p["url"]},
            raw_text=description,
        )
