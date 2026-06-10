"""Profile endpoints.

TODO(phase-1): persist profiles, trigger the profile-ingestion LangGraph flow
(résumé parse -> skills -> intents -> embeddings).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas.profile import (
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
    ResumeParseResult,
)

router = APIRouter()


@router.post("", response_model=ProfileOut, status_code=201)
def create_profile(payload: ProfileCreate) -> ProfileOut:
    raise HTTPException(status_code=501, detail="TODO(phase-1): create_profile")


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: uuid.UUID) -> ProfileOut:
    raise HTTPException(status_code=501, detail="TODO(phase-1): get_profile")


@router.patch("/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: uuid.UUID, payload: ProfileUpdate) -> ProfileOut:
    raise HTTPException(status_code=501, detail="TODO(phase-1): update_profile")


@router.post("/{profile_id}/resume", response_model=ResumeParseResult)
async def upload_resume(profile_id: uuid.UUID, file: UploadFile) -> ResumeParseResult:
    # TODO(phase-1): store blob (encrypted), enqueue parse job, return extraction.
    raise HTTPException(status_code=501, detail="TODO(phase-1): upload_resume")
