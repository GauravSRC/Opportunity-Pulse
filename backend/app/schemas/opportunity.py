"""Opportunity, explanation, and deadline schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DeadlineKind, Extractor, OpportunityType


class DeadlineOut(BaseModel):
    kind: DeadlineKind
    resolved_date: datetime | None = None
    anchor_text: str | None = None
    raw_phrase: str | None = None
    confidence: float
    needs_review: bool
    extractor: Extractor | None = None


class OpportunityOut(BaseModel):
    id: uuid.UUID
    title: str
    org: str | None
    type: OpportunityType
    location: str | None
    is_remote: bool
    url: str
    posted_at: datetime | None
    skills: list[str]
    score: float | None = None
    deadline: DeadlineOut | None = None
    also_seen_on: list[str] = []  # source URLs from the dedup cluster


class ScoreComponents(BaseModel):
    semantic: float = 0.0
    skill_overlap: float = 0.0
    recency: float = 0.0
    urgency: float = 0.0
    feedback: float = 0.0


class ExplanationOut(BaseModel):
    listing_id: uuid.UUID
    score: float
    components: ScoreComponents
    matched_skills: list[str] = []
    model_version: str


class DeadlineExtractRequest(BaseModel):
    text: str


class OpportunitySearchParams(BaseModel):
    q: str | None = None
    intent: str | None = None
    type: OpportunityType | None = None
    location: str | None = None
    remote: bool | None = None
    deadline_before: datetime | None = None
    sort: str = "score"
    page: int = 1
    limit: int = 20
