"""Outreach service: type-routed, grounded, draft-only artifact generation."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.enums import ArtifactStatus, ArtifactType as ModelArtifactType
from app.models.listing import NormalizedListing
from app.models.outreach import OutreachArtifact
from app.models.user import UserProfile
from app.services.profile_service import profile_to_dict
from email_agent.generators import generate as generate_draft
from email_agent.generators import self_check
from email_agent.rag import gather_context
from email_agent.router import route_artifact_type


def _listing_dict(ls: NormalizedListing) -> dict:
    return {
        "title": ls.title,
        "org": ls.org,
        "type": ls.type.value,
        "url": ls.url,
        "description": ls.description,
        "skills": ls.skills or [],
        "links_json": ls.links_json or {},
    }


def generate(db: Session, listing_id: uuid.UUID, user_id: uuid.UUID) -> OutreachArtifact:
    ls = db.get(NormalizedListing, listing_id)
    if ls is None:
        raise KeyError("listing not found")
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).one_or_none()
        if user_id
        else None
    )
    if profile is None:
        raise KeyError("profile not found")

    artifact_type = route_artifact_type(ls.type.value)  # cold_email ONLY for research
    context = gather_context(_listing_dict(ls), profile_to_dict(profile, profile.user), artifact_type)
    draft = self_check(generate_draft(artifact_type, context, profile_to_dict(profile, profile.user)), context)

    artifact = OutreachArtifact(
        user_id=user_id,
        listing_id=listing_id,
        artifact_type=ModelArtifactType(artifact_type.value),
        rag_sources_json={"sources": context["sources"]},
        subject=draft.get("subject"),
        body=draft["body"],
        status=ArtifactStatus.draft,
        grounding=draft.get("grounding", "unknown"),
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def update(db: Session, artifact_id: uuid.UUID, payload) -> OutreachArtifact:
    """payload: app.schemas.outreach.OutreachUpdate. Status limited to
    draft/approved/discarded — drafts are never auto-sent."""
    artifact = db.get(OutreachArtifact, artifact_id)
    if artifact is None:
        raise KeyError("artifact not found")
    if payload.body is not None:
        artifact.body = payload.body
    if payload.subject is not None:
        artifact.subject = payload.subject
    if payload.status is not None:
        artifact.status = ArtifactStatus(payload.status.value)
    db.commit()
    db.refresh(artifact)
    return artifact


def to_out(artifact: OutreachArtifact) -> dict:
    return {
        "id": artifact.id,
        "artifact_type": artifact.artifact_type.value,
        "subject": artifact.subject,
        "body": artifact.body,
        "rag_sources": (artifact.rag_sources_json or {}).get("sources", []),
        "status": artifact.status.value,
        "grounding": artifact.grounding,
    }
