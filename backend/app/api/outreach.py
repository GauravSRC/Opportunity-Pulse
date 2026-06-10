"""Outreach generation endpoints (type-routed).

The artifact type is decided server-side by email_agent.router from the
opportunity type — cold_email ONLY for research/lab, otherwise cover_letter /
sop / team_pitch / proposal / referral_note. Drafts are never auto-sent.
TODO(phase-4): wire the outreach LangGraph flow (route -> RAG -> draft -> HITL).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.schemas.outreach import OutreachOut, OutreachRequest, OutreachUpdate

router = APIRouter()


@router.post("/opportunities/{listing_id}/outreach", response_model=OutreachOut)
def generate_outreach(listing_id: uuid.UUID, payload: OutreachRequest) -> OutreachOut:
    # TODO(phase-4): look up listing.type -> route_artifact_type() -> RAG -> draft.
    raise HTTPException(status_code=501, detail="TODO(phase-4): generate_outreach")


@router.patch("/outreach/{artifact_id}", response_model=OutreachOut)
def update_outreach(artifact_id: uuid.UUID, payload: OutreachUpdate) -> OutreachOut:
    # Status may be draft/approved/discarded only — never "sent".
    raise HTTPException(status_code=501, detail="TODO(phase-4): update_outreach")
