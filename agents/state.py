"""Typed state objects passed through LangGraph nodes.

Each graph defines (or reuses) a TypedDict describing what flows between nodes.
Keeping these explicit makes the pipelines debuggable and testable without the
LLM in the loop.
"""

from __future__ import annotations

from typing import Any, TypedDict


class DiscoveryState(TypedDict, total=False):
    source_keys: list[str]
    raw_records: list[dict[str, Any]]
    normalized: list[dict[str, Any]]
    errors: list[dict[str, Any]]


class DedupRankState(TypedDict, total=False):
    user_id: str
    intent: str
    candidate_ids: list[str]
    clusters: list[dict[str, Any]]
    retrieved_ids: list[str]
    reranked_ids: list[str]
    scored: list[dict[str, Any]]  # [{listing_id, score, components}]
    over_latency_budget: bool


class DeadlineState(TypedDict, total=False):
    listing_id: str
    text: str
    kind: str
    resolved_date: str | None
    anchor_text: str | None
    raw_phrase: str | None
    confidence: float
    extractor: str
    needs_review: bool


class OutreachState(TypedDict, total=False):
    user_id: str
    listing_id: str
    listing_type: str
    artifact_type: str
    rag_context: list[dict[str, Any]]
    subject: str | None
    body: str
    grounding: str
    approved: bool


class FeedbackState(TypedDict, total=False):
    user_id: str
    signals: list[dict[str, Any]]
    updated_weights: dict[str, float]
    schedule_retrain: bool


class NotificationState(TypedDict, total=False):
    candidate_alerts: list[dict[str, Any]]
    scheduled: list[dict[str, Any]]
    dispatched: list[dict[str, Any]]
