"""Per-artifact draft generators (deterministic, grounded, draft-only).

Each generator turns RAG context + profile into an editable draft. Generation is
deterministic by default (reproducible, offline, no invented facts) and only
uses listing/profile facts gathered by rag.gather_context. An optional LLM
polish step can be enabled later; it is never required and never auto-sends.
"""

from __future__ import annotations

from email_agent.router import ArtifactType


def _skills_clause(facts: dict) -> str:
    ms = facts.get("matched_skills") or []
    return f"My background in {', '.join(ms)} aligns well with this." if ms else ""


def generate(artifact_type: ArtifactType, context: dict, profile: dict) -> dict:
    """Return {subject?, body, grounding}. Deterministic template fill."""
    f = context["facts"]
    grounding = context["grounding"]
    name = f.get("user_name") or "Your Name"
    org = f.get("org") or "your organization"
    title = f.get("title") or "the opportunity"
    skills_clause = _skills_clause(f)

    if artifact_type is ArtifactType.cold_email:
        subject = f"Prospective research with {org}"
        body = (
            f"Dear Professor,\n\n"
            f"I'm {name}, {f.get('user_headline') or 'a prospective researcher'}. "
            f"I've been following the work at {org} and am excited by the direction of "
            f"\"{title}\". {skills_clause}\n\n"
            f"I would be grateful for the opportunity to contribute to your lab. I've "
            f"attached my CV and can share relevant projects on request.\n\n"
            f"Thank you for your time and consideration.\n\nBest regards,\n{name}\n"
            f"{f.get('user_contact') or ''}".rstrip()
        )
        return {"subject": subject, "body": body, "grounding": grounding}

    if artifact_type is ArtifactType.cover_letter:
        body = (
            f"Dear Hiring Team at {org},\n\n"
            f"I'm excited to apply for {title}. {skills_clause}\n\n"
            f"In my recent work ({f.get('user_headline') or 'see attached CV'}), I built "
            f"and shipped projects directly relevant to this role, and I'm drawn to "
            f"{org}'s mission.\n\n"
            f"I'd welcome the chance to discuss how I can contribute. Thank you for your "
            f"consideration.\n\nSincerely,\n{name}"
        )
        return {"subject": None, "body": body, "grounding": grounding}

    if artifact_type is ArtifactType.sop:
        body = (
            f"# Statement of Purpose — {title}\n\n"
            f"## Motivation\nWhy {org} and {title} are the right fit for my goals.\n\n"
            f"## Background & preparation\n{f.get('user_headline') or '...'} {skills_clause}\n\n"
            f"## Goals & fit\nHow this program advances my objectives.\n\n"
            f"## Why me / why now\nWhat I uniquely contribute.\n"
        )
        return {"subject": None, "body": body, "grounding": grounding}

    if artifact_type is ArtifactType.team_pitch:
        body = (
            f"Looking for teammates for {title} ({org})!\n\n"
            f"Idea: a project aligned with the event theme.\n"
            f"What I bring: {', '.join(f.get('matched_skills') or ['full-stack skills'])}.\n"
            f"Looking for: complementary teammates. DM me — let's build something."
        )
        return {"subject": None, "body": body, "grounding": grounding}

    if artifact_type is ArtifactType.proposal:
        body = (
            f"# Proposal — {title} ({org})\n\n"
            f"## Summary\nA focused proposal for {title}.\n\n"
            f"## Approach & milestones\nConcrete, dated milestones.\n\n"
            f"## Relevant experience\n{f.get('user_headline') or '...'} {skills_clause}\n\n"
            f"## Mentor / contact note\nA short intro to the program contact."
        )
        return {"subject": None, "body": body, "grounding": grounding}

    # referral_note
    body = (
        f"Hi,\n\nI'm applying for {title} at {org} and your perspective would mean a lot. "
        f"Would you be open to a quick referral or a 10-minute chat?\n\n"
        f"No worries if you're busy — thank you either way!\n\n{name}"
    )
    return {"subject": None, "body": body, "grounding": grounding}


def self_check(draft: dict, context: dict) -> dict:
    """Flag ungrounded drafts. Deterministic generation only uses provided facts,
    so the main signal is how much real context backed the draft."""
    if context.get("grounding") == "low":
        draft = {**draft, "grounding": "low"}
    return draft
