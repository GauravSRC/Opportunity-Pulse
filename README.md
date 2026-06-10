<h1 align="center">OpportunityPulse</h1>

<p align="center">
  <b>A semantic, multi-agent platform that finds, dedups, ranks, and explains
  opportunities across 30+ sources — and drafts the right outreach for each.</b>
</p>

---

OpportunityPulse continuously discovers **jobs, internships, research/lab roles,
fellowships, hackathons, grants, conferences, and GSoC-like programs** from many
sources, normalizes them into one schema, removes cross-source duplicates,
extracts messy/fuzzy deadlines, models urgency and decay, and ranks everything
against a persistent user profile with an **explainable** match score. For each
opportunity it drafts the *appropriate* outreach artifact — a cold email for a
professor's lab, a tailored cover letter for a company job, an SOP outline for a
fellowship, a team pitch for a hackathon.

It is designed to feel like a real product students use every week — not a demo.

## Why it exists

Finding opportunities is a scattered, manual, multi-hour weekly chore. Listings
are duplicated across sites, deadlines hide in prose ("rolling until filled"),
and writing outreach from a blank page is exhausting. OpportunityPulse collapses
that into one personalized, deadline-aware, explainable feed with action-ready
drafts.

## Key features

- **Semantic matching** against your profile using embeddings (not keyword-only).
- **Cross-source deduplication** via blocking + embeddings + fuzzy matching.
- **Fuzzy deadline NLP** that handles relative phrases ("two weeks before demo
  day", "rolling admission until filled", "end of quarter").
- **Urgency / decay model** estimating how soon an opportunity is likely to close.
- **Type-routed outreach** — cold email *only* for research/lab roles; cover
  letter / SOP / team pitch / proposal otherwise. Always human-approved, never
  auto-sent.
- **Explainable ranking** — every score breaks down into semantic, skill,
  recency, and urgency components.
- **Alerts & reminders** for high-fit, soon-to-close opportunities.
- **Chrome extension** that shows your live match score on a listing page.

## Architecture at a glance

`Next.js web + Chrome extension` -> `FastAPI (sync reads)` -> `Redis queue` ->
`Arq workers running LangGraph agent pipelines` -> `PostgreSQL + pgvector`,
with `LangSmith + Prometheus` for observability. See
[`ARCHITECTURE.md`](ARCHITECTURE.md).

## Quick start (Phase 0 scaffold)

```bash
cp .env.example .env          # fill in keys (Anthropic/OpenAI/search/GitHub/Kaggle)
docker compose up -d db redis # Postgres+pgvector and Redis
docker compose config         # validate the full compose file
# Backend (later phases): cd backend && uvicorn app.main:app --reload
# Web (later phases):      cd web && npm install && npm run dev
```

## Documentation

- [`PROJECT.md`](PROJECT.md) — full end-to-end design and workflow.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system map and data flow.
- [`CLAUDE.md`](CLAUDE.md) — contributor/agent guide and conventions.
- [`docs/`](docs/) — deep-dives: data model, ML design, agents, sourcing, API,
  evaluation, roadmap, interview framing.

## Status & roadmap

Phase 0 (scaffold) is in place. Phases 1–7 (MVP -> ranking+dedup -> deadline
intelligence -> outreach agent -> extension -> learning loop -> production
hardening) are tracked in [`docs/roadmap.md`](docs/roadmap.md).

## Legal / ethical

We honor `robots.txt` and source Terms of Service, prefer official/structured
endpoints over scraping, never scrape login-walled or paid data, store
provenance for every listing, encrypt user PII at rest, and never auto-send
outreach. See [`docs/sourcing.md`](docs/sourcing.md).

## License

MIT — see [`LICENSE`](LICENSE).
