"""Profile onboarding service: create/update user + profile, skills, embeddings."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EmbeddingOwner
from app.models.user import Skill, User, UserProfile
from app.services.embeddings import store_embedding
from ingestion.normalize import extract_skills
from ranking.embedder import embed_profile


def profile_to_dict(profile: UserProfile, user: User | None = None) -> dict:
    return {
        "headline": profile.headline,
        "skills": [s.canonical_name for s in profile.skills],
        "intents": list(profile.intents or []),
        "locations": list(profile.locations or []),
        "experience_json": profile.experience_json or {},
        "email": user.email if user else None,
        "name": (profile.headline or (user.email.split("@")[0] if user else "")),
    }


def _get_or_create_user(db: Session, email: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        user = User(email=email)
        db.add(user)
        db.flush()
    return user


def _attach_skills(db: Session, names: list[str]) -> list[Skill]:
    skills: list[Skill] = []
    for name in dict.fromkeys(n.strip() for n in names if n and n.strip()):
        skill = db.execute(
            select(Skill).where(Skill.canonical_name == name)
        ).scalar_one_or_none()
        if skill is None:
            skill = Skill(canonical_name=name, aliases=[])
            db.add(skill)
            db.flush()
        skills.append(skill)
    return skills


def _embed_and_store(db: Session, profile: UserProfile, user: User) -> None:
    vectors = embed_profile(profile_to_dict(profile, user))
    for intent, vec in vectors.items():
        store_embedding(
            db,
            EmbeddingOwner.profile,
            profile.id,
            vec,
            intent=None if intent == "_all" else intent,
        )


def create_profile(db: Session, payload) -> UserProfile:
    """payload: app.schemas.profile.ProfileCreate"""
    user = _get_or_create_user(db, payload.email)
    profile = user.profile or UserProfile(user_id=user.id)
    profile.headline = payload.headline
    profile.intents = [i.value for i in payload.intents]
    profile.locations = payload.locations
    profile.is_remote_ok = payload.is_remote_ok
    profile.education_json = payload.education or {}
    profile.experience_json = payload.experience or {}
    profile.preferences_json = payload.preferences or {}
    profile.skills = _attach_skills(db, payload.skills)
    db.add(profile)
    db.flush()
    _embed_and_store(db, profile, user)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile_id: uuid.UUID, payload) -> UserProfile:
    """payload: app.schemas.profile.ProfileUpdate"""
    profile = db.get(UserProfile, profile_id)
    if profile is None:
        raise KeyError("profile not found")
    if payload.headline is not None:
        profile.headline = payload.headline
    if payload.intents is not None:
        profile.intents = [i.value for i in payload.intents]
    if payload.locations is not None:
        profile.locations = payload.locations
    if payload.is_remote_ok is not None:
        profile.is_remote_ok = payload.is_remote_ok
    if payload.preferences is not None:
        profile.preferences_json = payload.preferences
    if payload.skills is not None:
        profile.skills = _attach_skills(db, payload.skills)
    db.flush()
    _embed_and_store(db, profile, profile.user)
    db.commit()
    db.refresh(profile)
    return profile


def ingest_resume(db: Session, profile_id: uuid.UUID, raw_bytes: bytes) -> dict:
    """Extract skills from résumé text (best-effort) and merge into the profile."""
    profile = db.get(UserProfile, profile_id)
    if profile is None:
        raise KeyError("profile not found")
    text = raw_bytes.decode("utf-8", errors="ignore")
    found = extract_skills(text)
    if found:
        existing = {s.canonical_name for s in profile.skills}
        merged = sorted(existing | set(found))
        profile.skills = _attach_skills(db, merged)
        db.flush()
        _embed_and_store(db, profile, profile.user)
    db.commit()
    return {"parsed": True, "skills": found, "note": f"extracted {len(found)} skills"}
