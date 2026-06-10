# Implementation roadmap

Phase-gated and solo-buildable. Each phase ends with something demoable.

## Phase 0 — Project setup  *(complexity: S)*
- **Goals:** runnable skeleton, infra, schema, CI.
- **Tasks:** monorepo scaffold; docker-compose (Postgres+pgvector, Redis);
  `.env.example`; base SQLAlchemy models + initial Alembic migration; CI lint+test.
- **Deliverables:** `docker compose up -d db redis` healthy; `alembic upgrade
  head` applies schema; `pytest` collects.
- **Dependencies:** none.
- **Demo:** healthchecks + OpenAPI docs page.

## Phase 1 — MVP  *(complexity: M)*
- **Goals:** real ranked feed from real sources.
- **Tasks:** profile ingestion (résumé+form); 5–8 ATS/API adapters (Greenhouse,
  Lever, GitHub, Remotive, HN, Adzuna, arXiv); normalize; bi-encoder embeddings +
  pgvector retrieval; recency signal; feed API + minimal Next.js feed;
  save/dismiss; basic deadline rules; explanation chips.
- **Deliverables:** end-to-end feed for a test profile.
- **Dependencies:** Phase 0.
- **Demo:** ranked feed with score chips from live sources.

## Phase 2 — Intelligent ranking + dedup  *(complexity: M-L)*
- **Goals:** precision + de-duplicated feed.
- **Tasks:** blocking + embedding/fuzzy similarity + union-find clustering +
  metadata merge; cross-encoder rerank (latency-gated); full score blend +
  explanation panel; "also seen on" UI.
- **Deliverables:** dedup clusters; explainable ranking.
- **Dependencies:** Phase 1.
- **Demo:** duplicate listings merged; "why it matched" panel.

## Phase 3 — Deadline intelligence + reminders  *(complexity: M-L)*
- **Goals:** trustworthy deadlines + urgency.
- **Tasks:** rules→NER→LLM ladder + confidence + review queue; decay/urgency
  model; alert rules; email/in-app alerts; calendar (.ics) export.
- **Deliverables:** deadline tracker; reminders.
- **Dependencies:** Phase 1 (2 helpful).
- **Demo:** urgency-sorted tracker + a fired reminder.

## Phase 4 — Cold email / outreach agent  *(complexity: M)*
- **Goals:** type-routed, grounded drafts.
- **Tasks:** artifact router; RAG over lab pages + papers (and company/program
  pages); draft + self-check; HITL approval UI; provenance display.
- **Deliverables:** outreach generator wired to the feed.
- **Dependencies:** Phases 1–2.
- **Demo:** cold email for a lab vs cover letter for a company job — *same button,
  different artifact*.

## Phase 5 — Chrome extension + overlay  *(complexity: M)*
- **Goals:** in-page match score.
- **Tasks:** MV3 content script badge; popup with breakdown + "save"; auth token
  handshake with backend.
- **Deliverables:** unpacked extension.
- **Dependencies:** Phases 1–2.
- **Demo:** live match badge on a real listing page.

## Phase 6 — Learning loop + observability  *(complexity: M)*
- **Goals:** ranking improves with use; everything observable.
- **Tasks:** feedback signals → online weight updates + offline retrain;
  LangSmith tracing; Prometheus metrics; eval harness wired to CI.
- **Deliverables:** metrics dashboard; eval reports.
- **Dependencies:** Phases 1–4.
- **Demo:** ranking shifts after feedback; dashboards.

## Phase 7 — Production hardening  *(complexity: M-L)*
- **Goals:** safe, reliable, deployed.
- **Tasks:** auth hardening; rate limits; source-health auto-disable; backups;
  deploy workflow (Fly.io); load/latency tuning; data export/delete.
- **Deliverables:** live URL; runbook.
- **Dependencies:** all prior.
- **Demo:** public deployment.

## Suggested order for a solo dev

0 → 1 → 2 → 4 (outreach is a strong demo early) → 3 → 5 → 6 → 7, adjusting to
whatever you want to show in a given interview week.
