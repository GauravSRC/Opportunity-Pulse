"""Outreach (type-routed) schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.enums import ArtifactStatus, ArtifactType


class OutreachRequest(BaseModel):
    user_id: uuid.UUID
    tone: str | None = None
    regenerate: bool = False


class RagSource(BaseModel):
    kind: str  # lab_page | paper | company_page | program_page | event_page ...
    url: str


class OutreachOut(BaseModel):
    id: uuid.UUID | None = None
    artifact_type: ArtifactType
    subject: str | None = None
    body: str
    rag_sources: list[RagSource] = []
    status: ArtifactStatus = ArtifactStatus.draft
    grounding: str = "unknown"  # high | medium | low


class OutreachUpdate(BaseModel):
    body: str | None = None
    subject: str | None = None
    status: ArtifactStatus | None = None  # never "sent" — drafts are not auto-sent
