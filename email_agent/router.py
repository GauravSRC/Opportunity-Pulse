"""Outreach artifact router — the core product rule.

Maps an opportunity type to the correct outreach artifact. A ``cold_email`` is
produced ONLY for research/lab/professor opportunities. The web app renders
whatever this returns; it must never assume "cold email" as a default.

This routing is deterministic and fully implemented (it is product logic, not
ML). The downstream RAG + drafting is stubbed for Phase 4.
"""

from __future__ import annotations

from enum import Enum


class ArtifactType(str, Enum):
    cold_email = "cold_email"
    cover_letter = "cover_letter"
    sop = "sop"
    team_pitch = "team_pitch"
    proposal = "proposal"
    referral_note = "referral_note"


# Opportunity type (see app.models.enums.OpportunityType) -> artifact.
_ROUTING: dict[str, ArtifactType] = {
    "research": ArtifactType.cold_email,     # professor / lab -> cold email ONLY here
    "job": ArtifactType.cover_letter,
    "internship": ArtifactType.cover_letter,
    "fellowship": ArtifactType.sop,
    "grant": ArtifactType.proposal,
    "hackathon": ArtifactType.team_pitch,
    "gsoc": ArtifactType.proposal,
    "conference": ArtifactType.sop,
}

# Default for any unrecognized type: a neutral cover letter (never a cold email).
_DEFAULT = ArtifactType.cover_letter


def route_artifact_type(opportunity_type: str) -> ArtifactType:
    """Return the outreach artifact type for the given opportunity type.

    >>> route_artifact_type("research")
    <ArtifactType.cold_email: 'cold_email'>
    >>> route_artifact_type("internship")
    <ArtifactType.cover_letter: 'cover_letter'>
    """
    return _ROUTING.get((opportunity_type or "").lower(), _DEFAULT)


def is_cold_email_allowed(opportunity_type: str) -> bool:
    """True only for research/lab/professor opportunities."""
    return route_artifact_type(opportunity_type) is ArtifactType.cold_email
