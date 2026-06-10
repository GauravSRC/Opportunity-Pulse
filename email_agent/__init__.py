"""Type-routed outreach generation.

The artifact depends on the opportunity type — a cold email is produced ONLY
for research/lab/professor opportunities; everything else gets a cover letter,
SOP, team pitch, proposal, or referral note. See router.py and docs/ml-design.md
section 9. Drafts are always human-approved and never auto-sent.
"""

from __future__ import annotations

from email_agent.router import ArtifactType, route_artifact_type

__all__ = ["ArtifactType", "route_artifact_type"]
