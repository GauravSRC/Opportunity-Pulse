"""Enumerations shared across models and schemas."""

from __future__ import annotations

import enum


class AuthProvider(str, enum.Enum):
    local = "local"
    google = "google"
    github = "github"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class Intent(str, enum.Enum):
    research = "research"
    internship = "internship"
    job = "job"
    fellowship = "fellowship"
    hackathon = "hackathon"
    grant = "grant"


class OpportunityType(str, enum.Enum):
    job = "job"
    internship = "internship"
    research = "research"
    fellowship = "fellowship"
    hackathon = "hackathon"
    grant = "grant"
    conference = "conference"
    gsoc = "gsoc"


class AccessMethod(str, enum.Enum):
    api = "api"
    ats_json = "ats_json"
    rss = "rss"
    sitemap = "sitemap"
    search = "search"
    browser = "browser"


class RawStatus(str, enum.Enum):
    new = "new"
    normalized = "normalized"
    error = "error"


class DeadlineKind(str, enum.Enum):
    fixed = "fixed"
    rolling = "rolling"
    relative = "relative"
    unknown = "unknown"


class Extractor(str, enum.Enum):
    rule = "rule"
    ner = "ner"
    llm = "llm"


class ArtifactType(str, enum.Enum):
    """Outreach artifact types. Chosen by the router from the opportunity type.

    ``cold_email`` is produced ONLY for research/lab/professor opportunities.
    See email_agent/router.py.
    """

    cold_email = "cold_email"
    cover_letter = "cover_letter"
    sop = "sop"
    team_pitch = "team_pitch"
    proposal = "proposal"
    referral_note = "referral_note"


class ArtifactStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    discarded = "discarded"


class FeedbackSignal(str, enum.Enum):
    click = "click"
    save = "save"
    dismiss = "dismiss"
    thumbs_up = "thumbs_up"
    thumbs_down = "thumbs_down"
    applied = "applied"


class AlertChannel(str, enum.Enum):
    inapp = "inapp"
    email = "email"
    calendar = "calendar"


class AlertStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    suppressed = "suppressed"


class EmbeddingOwner(str, enum.Enum):
    profile = "profile"
    listing = "listing"
    skill = "skill"
