"""Tests for the outreach artifact router — the core product rule.

Cold email MUST be produced only for research/lab opportunities; everything
else gets a different artifact.
"""

from __future__ import annotations

import pytest

from email_agent.router import ArtifactType, is_cold_email_allowed, route_artifact_type


def test_research_routes_to_cold_email():
    assert route_artifact_type("research") is ArtifactType.cold_email
    assert is_cold_email_allowed("research") is True


@pytest.mark.parametrize(
    "opp_type, expected",
    [
        ("job", ArtifactType.cover_letter),
        ("internship", ArtifactType.cover_letter),
        ("fellowship", ArtifactType.sop),
        ("grant", ArtifactType.proposal),
        ("hackathon", ArtifactType.team_pitch),
        ("gsoc", ArtifactType.proposal),
        ("conference", ArtifactType.sop),
    ],
)
def test_non_research_never_cold_email(opp_type, expected):
    assert route_artifact_type(opp_type) is expected
    assert is_cold_email_allowed(opp_type) is False


def test_unknown_type_defaults_to_cover_letter_not_cold_email():
    assert route_artifact_type("something_new") is ArtifactType.cover_letter
    assert is_cold_email_allowed("") is False
