"""Profile endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.profile import (
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
    ResumeParseResult,
)
from app.services import profile_service

router = APIRouter()


def _profile_out(profile) -> ProfileOut:
    return ProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        headline=profile.headline,
        skills=[s.canonical_name for s in profile.skills],
        intents=list(profile.intents or []),
        locations=list(profile.locations or []),
        is_remote_ok=bool(profile.is_remote_ok),
    )


@router.post("", response_model=ProfileOut, status_code=201)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)) -> ProfileOut:
    try:
        profile = profile_service.create_profile(db, payload)
        return _profile_out(profile)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> ProfileOut:
    from app.models.user import UserProfile
    profile = db.get(UserProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_out(profile)


@router.patch("/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: uuid.UUID, payload: ProfileUpdate, db: Session = Depends(get_db)) -> ProfileOut:
    try:
        profile = profile_service.update_profile(db, profile_id, payload)
        return _profile_out(profile)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{profile_id}/resume", response_model=ResumeParseResult)
async def upload_resume(profile_id: uuid.UUID, file: UploadFile, db: Session = Depends(get_db)) -> ResumeParseResult:
    try:
        raw = await file.read()
        result = profile_service.ingest_resume(db, profile_id, raw)
        return ResumeParseResult(
            parsed=result["parsed"],
            skills=result.get("skills", []),
            note=result.get("note"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
