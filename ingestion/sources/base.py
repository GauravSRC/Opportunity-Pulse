"""Source adapter contract + canonical data shapes.

Every adapter subclasses ``SourceAdapter``. Adapters MUST be schema-tolerant
(never assume a field exists), MUST NOT raise on a single bad record (skip and
count a parse error), and MUST emit a ``NormalizedListing``. See docs/sourcing.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AccessMethod(str, Enum):
    api = "api"
    ats_json = "ats_json"
    rss = "rss"
    sitemap = "sitemap"
    search = "search"
    browser = "browser"


@dataclass
class RawRecord:
    """A raw item as fetched from a source, before normalization."""

    external_id: str
    url: str
    payload: dict
    fetched_at: datetime


@dataclass
class NormalizedListing:
    """Canonical listing shape consumed by all downstream stages."""

    source_key: str
    external_id: str
    title: str
    url: str
    type: str  # OpportunityType value
    org: str | None = None
    location: str | None = None
    is_remote: bool = False
    posted_at: datetime | None = None
    description: str | None = None
    skills: list[str] = field(default_factory=list)
    links: dict = field(default_factory=dict)  # {lab_page, paper_urls[], apply_url, contact_email?}
    raw_text: str | None = None


class SourceAdapter(ABC):
    """Base class for all source adapters."""

    key: str
    access_method: AccessMethod
    category: str

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> list[RawRecord]:
        """Pull raw records (respecting rate limits / conditional GET)."""
        raise NotImplementedError

    @abstractmethod
    def parse(self, record: RawRecord) -> NormalizedListing | None:
        """Map one raw record to a NormalizedListing, or None to skip it."""
        raise NotImplementedError
