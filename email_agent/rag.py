"""Retrieval-augmented context for outreach drafting.

Gathers grounding context appropriate to the artifact type:
  - cold_email (research): lab page + recent papers (arXiv/OpenAlex) + user projects
  - cover_letter (job/internship): company page + JD + user experience
  - sop/proposal (fellowship/grant/gsoc): program/org page + user goals/OSS history
  - team_pitch (hackathon): event page + theme + user skills

Returns provenance so the UI can show what grounded the draft. Cached per
listing. See docs/ml-design.md section 9.
"""

from __future__ import annotations

from email_agent.router import ArtifactType


def gather_context(listing: dict, profile: dict, artifact_type: ArtifactType) -> dict:
    """Return {sources: [{kind, url}], chunks: [...], grounding: high|medium|low}.

    TODO(phase-4): fetch + split + retrieve relevant chunks via LangChain
    loaders/splitters and the search provider; dedupe; cap context size.
    """
    raise NotImplementedError("gather_context")
