# OpportunityPulse — End-to-End Project Design

> The complete design and workflow document. Companion files:
> [`ARCHITECTURE.md`](ARCHITECTURE.md) (system map), [`CLAUDE.md`](CLAUDE.md)
> (contributor guide), and [`docs/`](docs/) (module deep-dives). Where a section
> here is summarized, the matching `docs/*.md` carries the long form.

## Table of contents

1. [Product definition](#1-product-definition)
2. [Feature set](#2-feature-set)
3. [System architecture](#3-system-architecture)
4. [Data sourcing strategy](#4-data-sourcing-strategy)
5. [Data model](#5-data-model)
6. [ML / AI design](#6-ml--ai-design)
7. [Agent orchestration](#7-agent-orchestration)
8. [Frontend / UX](#8-frontend--ux)
9. [API design](#9-api-design)
10. [Evaluation & metrics](#10-evaluation--metrics)
11. [Tech stack & rationale](#11-tech-stack--rationale)
12. [Implementation roadmap](#12-implementation-roadmap)
13. [Repository structure](#13-repository-structure)
14. [Interview framing](#14-interview-framing)
15. [Practical constraints & tradeoffs](#15-practical-constraints--tradeoffs)

---

## 1. Product definition

**Summary.** OpportunityPulse is a semantic, multi-agent platform that
continuously discovers opportunities across 30+ sources, normalizes them into a
single schema, deduplicates the same listing seen on many sites, extracts and
interprets fuzzy deadlines, ranks everything against a persistent user profile
with an *explainable* score, warns about decaying/expiring chances, and drafts
the appropriate outreach artifact for each opportunity type.

**Target users.**
- **Students** seeking internships, research positions, fellowships, hackathons,
  and grants.
- **Early-career job seekers** who want signal over noise.
- **Researchers** seeking labs, funding, visiting positions, and collaborations.

**Main user journeys.**
1. **Onboard** → upload résumé + pick skills/intents/locations → ranked feed in
   minutes.
2. **Discover** → browse feed → open a listing → read *why it matched* → save or
   dismiss (which teaches the ranker).
3. **Stay on time** → deadline tracker sorted by urgency → add to calendar →
   receive reminders before close.
4. **Reach out** → on a research/lab listing, generate a context-grounded cold
   email; on a company job, a tailored cover letter; on a fellowship, an SOP
   outline — always editable, always human-approved.
5. **Get alerted** → high-fit + soon-to-close opportunities surface proactively.
6. **In-browser** → the extension shows a live match score on a listing page.

**Core pain points solved.** Scattered sources; keyword search that misses
intent; duplicate listings; deadlines buried in prose; no sense of urgency;
blank-page paralysis writing outreach; tools that never remember what you want.

**Why it matters.** It turns a recurring, stressful, multi-hour weekly hunt into
one personalized, explainable, deadline-aware feed with action-ready drafts —
useful every single week, not just impressive once.

---

## 2. Feature set

### MVP
- Profile from résumé upload + structured form (skills, intents, locations).
- 5–8 robust sources (ATS JSON + official APIs — the least brittle).
- Unified normalized schema.
- Bi-encoder semantic match + recency signal.
- Ranked feed with save/dismiss.
- Basic deadline parsing (absolute dates + simple relative phrases).
- Explainable score chips (semantic / skill / recency).

### V1
- 20+ sources across all categories.
- Cross-source deduplication with clustering.
- Cross-encoder reranking (precision second stage).
- Fuzzy/relative deadline NLP with confidence + human review queue.
- Decay / urgency model.
- **Type-routed outreach generator** with RAG (cold email / cover letter / SOP /
  team pitch / proposal / referral note).
- In-app + email alerts; calendar export.
- Feedback learning loop.
- LangSmith tracing + evaluation harness.

### Stretch
- Chrome extension overlay + popup.
- Two-way calendar sync.
- Bandit re-ranking with exploration.
- Multilingual sources.
- Saved-search agents and weekly digest email.
- "Similar opportunities"; lab/team graph for warm intros.

### Excluded for now (deliberate)
- Auto-sending outreach (draft-only, human-in-the-loop only).
- Reddit (no API access; respect that constraint).
- Paid job-board resale data; login-walled scraping.
- Native mobile app; auto-apply bots.

### Impressive-but-realistic (interview leverage)
Explainable ranking traces, dedup clustering, the fuzzy-deadline fallback
ladder, decay modeling, and an eval harness combining offline + online + human
review — all achievable solo, all defensible under questioning.

---

## 3. System architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the diagram. Highlights:

- **Sync** path (FastAPI): user-facing reads — search, detail, explanation,
  feed, on-demand draft. Returns precomputed rank scores; never blocks on heavy
  ML.
- **Async** path (Arq workers over Redis): discovery, normalization, dedup,
  embedding, batch ranking refresh, decay recompute, alert dispatch — scheduled,
  retryable, fan-out.

**Agents.**

| Agent | Consumes | Produces | Sync/Async |
|---|---|---|---|
| Profile | résumé, form, feedback | `user_profiles`, profile vectors | sync edit / async parse |
| Discovery (per source type) | source registry | `raw_listings` | async (cron+queue) |
| Normalize | `raw_listings` | `normalized_listings` | async |
| Dedup | normalized listings | `dedup_clusters`, canonical record | async |
| Deadline | listing text | `deadlines` (+confidence) | async |
| Ranking | profile + listings + feedback | `rank_scores` + explanation | async batch / sync read |
| Decay | deadlines, posting age, source velocity | urgency scores | async |
| Outreach | listing + profile + RAG context | `outreach_artifacts` | sync on demand, HITL |
| Alert | rank + deadlines + rules | `alerts` | async |
| Feedback/Learning | signals | updated ranking weights | async |

**Communication.** REST for client↔backend; Redis queue (jobs) + Postgres
(state) for backend↔workers; a typed `GraphState` flows through LangGraph nodes;
LangSmith captures traces.

**LangGraph vs LangChain.** LangGraph orchestrates stateful, branching,
retryable, human-in-the-loop flows (the discovery→…→rank pipeline; outreach with
its approval gate; the feedback loop). LangChain is used **narrowly** — document
loaders, text splitters, retriever wrappers, and the LLM provider abstraction —
and explicitly **not** for plain HTTP/DB calls, the ranking math, dedup, or
deadline rules, which stay as transparent, unit-testable Python. Full rationale
in [`docs/agents.md`](docs/agents.md).

---

## 4. Data sourcing strategy

**Guiding principle.** Prefer structured, ToS-friendly endpoints; scrape only as
a last resort; always check `robots.txt` and ToS; identify the crawler; respect
rate limits; cache aggressively. Per-source fallback ladder:

```
Official API  →  ATS JSON  →  RSS/Atom  →  sitemap.xml  →  search API  →  Playwright
```

**30+ source categories** (with primary access method) are enumerated in
[`docs/sourcing.md`](docs/sourcing.md) and configured in
[`ingestion/registry.yaml`](ingestion/registry.yaml). Representative set:
Greenhouse / Lever / Ashby (ATS JSON), GitHub good-first-issue + GSoC orgs
(GitHub API), Kaggle competitions (Kaggle API), Devpost / MLH (feeds), arXiv +
OpenAlex/Crossref (APIs, for research-active labs), university/lab pages
(RSS/sitemap/scrape), WikiCFP (RSS), grants.gov + EU CORDIS (APIs), USAJobs /
Adzuna / Remotive / RemoteOK (APIs), HN "Who is hiring" (Algolia API), plus
generic RSS, generic sitemap, and a Tavily/SerpAPI web-discovery adapter.

**Anti-brittleness.**
- Thin **per-source adapter** implementing one interface
  (`fetch → parse → emit RawListing`); config in `registry.yaml`.
- **Content-fingerprint** change detection; idempotent ingestion.
- **Source-health monitor** tracking success rate, parse-error rate, and
  freshness lag; auto-disables a flapping source and raises an alert.
- **Schema-tolerant parsing** — never assume a field exists.
- **Rate / anti-bot**: per-host token-bucket limiter, exponential backoff +
  jitter, identifying user-agent, conditional GET (ETag / If-Modified-Since),
  Playwright pool reserved for JS-required pages only.
- **Normalization**: every adapter emits the canonical `NormalizedListing`
  (title, org, type, location/remote, url, source, posted_at, raw_text,
  skills[], links{}) so everything downstream is source-agnostic.

**Legal / ethical.** Honor robots + ToS; no login-walled or paid-data scraping;
store source + retrieval timestamp for provenance; outreach is never auto-sent;
user PII (résumé) is encrypted at rest; data export/delete is supported. Human
review is required for low-confidence deadlines, borderline dedup pairs, and all
outreach drafts.

---

## 5. Data model

Full DDL-level detail in [`docs/data-model.md`](docs/data-model.md). All tables
carry `id uuid` PK and `created_at` / `updated_at`. Core entities:

- **users** — email, auth_provider, hashed_pw/oauth_sub, role, settings_json.
- **skills** — canonical_name, aliases[], category, embedding_id.
- **user_profiles** — user_id, headline, education_json, experience_json,
  skills[], intents[] (`research|internship|job|fellowship|hackathon|grant`),
  locations[], resume_blob_ref, preferences_json.
- **opportunity_sources** — key, name, category, access_method, base_url,
  config_json, enabled, health_json, last_run_at.
- **raw_listings** — source_id, external_id, url, fetched_at, payload_json,
  content_fingerprint, status.
- **normalized_listings** — raw_id, source_id, title, org, type, location,
  is_remote, url, posted_at, description, skills[], links_json, cluster_id,
  is_canonical.
- **deadlines** — listing_id, kind (`fixed|rolling|relative|unknown`),
  resolved_date, anchor_text, raw_phrase, confidence, needs_review, extractor.
- **rank_scores** — user_id, listing_id, score, components_json, model_version,
  computed_at.
- **dedup_clusters** — canonical_listing_id, member_ids[], method_json,
  confidence, merged_metadata_json.
- **outreach_artifacts** — user_id, listing_id, artifact_type
  (`cold_email|cover_letter|sop|team_pitch|proposal|referral_note`),
  rag_sources_json, subject, body, status (`draft|approved|discarded`),
  model_version.
- **feedback** — user_id, listing_id, signal, weight, context_json.
- **alerts** — user_id, listing_id, rule, channel, scheduled_for, sent_at,
  status.
- **embeddings** — owner_type (`profile|listing|skill`), owner_id, model, dim,
  vector (pgvector), HNSW index.
- **audit_logs** — actor, action, entity, entity_id, meta_json, ts.

---

## 6. ML / AI design

Deep version in [`docs/ml-design.md`](docs/ml-design.md). Summary:

- **Profile embedding.** Structured profile → templated NL doc → bi-encoder.
  **Multi-intent**: one vector per intent so research vs. job queries rank
  differently. Default `BAAI/bge-small-en-v1.5`; `all-mpnet-base-v2` or hosted
  embeddings swappable by env.
- **Opportunity embedding.** `title + org + type + skills + summary` → same
  space → pgvector + HNSW.
- **Retrieval.** Cosine top-K per intent vector. *Baseline*: single vector +
  BM25 hybrid. *Advanced*: multi-intent + reciprocal-rank fusion of dense+lexical.
- **Reranker (optional).** Cross-encoder `ms-marco-MiniLM-L-6-v2` over top-K,
  gated by a latency budget.
- **Query expansion.** LLM expands sparse intents into skill/term sets used for
  retrieval *and* discovery search queries.
- **Deduplication.** Block by canonical URL + normalized title/org → candidate
  pairs → embedding cosine + `rapidfuzz` similarity → threshold → union-find
  clusters → metadata merge (richest fields, union skills, earliest posted_at,
  all source URLs).
- **Deadline extraction (fallback ladder).** (1) rules — `dateparser` + regex for
  absolute and common relative phrases, with "rolling until filled" →
  `kind=rolling`; (2) spaCy NER / pattern matcher; (3) LLM fallback for fuzzy /
  anchored phrases ("two weeks before demo day" → store `anchor_text`, flag
  `needs_anchor`). Each emits a confidence; below threshold → `needs_review`.
- **Decay / urgency.** *Baseline*: exponential decay over `time_to_deadline`,
  `posting_age`, `source_velocity`, with `rolling` handled specially.
  *Advanced*: logistic regression / survival model on observed "still open?"
  labels harvested over time.
- **Outreach generation (RAG, type-routed).** The artifact router keys off
  `listing.type`:
  - research/lab/professor → **cold email** (RAG over lab page + recent papers +
    user's relevant projects);
  - company job/internship → **cover letter / referral note**;
  - fellowship/scholarship/grant → **SOP / motivation outline**;
  - hackathon → **team-up pitch / project brief**;
  - GSoC/OSS → **proposal outline + mentor intro**;
  - conference → **submission / travel-grant note**.

  So a cold-email draft appears **only** for a professor/lab role; everything
  else gets its correct artifact. Always HITL; never auto-sent.
- **Feedback-based ranking.** Implicit (click/save/dismiss/apply) + explicit
  (thumbs) → per-user online logistic-regression / bandit updates on the
  score-blend coefficients; periodic offline retrain; an exploration term guards
  against filter-bubble collapse.
- **Evaluation & fallbacks.** Every ML stage has a deterministic fallback so the
  product degrades gracefully (rules-only deadlines if the LLM is down; lexical
  search if embeddings fail; prior weights if retrain fails). Metrics in §10.

---

## 7. Agent orchestration

LangGraph flows (nodes / edges / branching / retries / failure / HITL / caching)
detailed in [`docs/agents.md`](docs/agents.md):

1. **Profile ingestion** — `receive → parse_resume → extract_skills →
   build_intents → embed → persist`. Branch: parse fail → form-only. Retry parse
   ×2. Cache embeddings by content hash.
2. **Discovery** — `select_sources → fan-out adapters → fetch → parse →
   emit_raw → normalize`. Per-adapter retry+backoff; failure isolates + marks
   source health. Cache via ETag/fingerprint.
3. **Dedup + ranking** — `load_new → block → pairwise_sim → cluster → merge →
   embed_canonical → retrieve → rerank → score → explain → persist`. Branch:
   skip reranker if over latency budget. Cache embeddings.
4. **Deadline update** — `collect_text → rules → (conf<θ?) ner → (conf<θ?) llm →
   confidence → persist | review_queue`. HITL = review queue. Retry LLM ×2 →
   `unknown`.
5. **Outreach (on-demand)** — `route_by_type → retrieve_context(RAG) → draft →
   self_check → present_for_approval`. **HITL gate** before save/approve; never
   sends. Cache RAG context per listing.
6. **Feedback learning** — `collect_signals → update_weights(online) →
   (threshold?) schedule_offline_retrain`. Failure → keep prior weights.
7. **Notification** — `eval_rules → dedupe_alerts → schedule → dispatch →
   record`. Retry dispatch ×3 → in-app fallback.

---

## 8. Frontend / UX

See [`web/README.md`](web/README.md). Screens:

- **Onboarding** — résumé drop + skill/intent chips + location/remote prefs →
  instant first feed.
- **Feed** — ranked cards (title, org, type, deadline urgency badge, match %)
  with filter (type/location/remote/deadline) + sort.
- **Detail + "Why it matched"** — component bars (semantic, skills, recency,
  urgency) + matched-skill highlights + dedup "also seen on" sources.
- **Saved / dismissed**; **Deadline tracker** (urgency-sorted, add-to-calendar).
- **Outreach generator** — shows *only the artifact type that fits the listing*;
  editable; copy/export; approval state.
- **Alert settings**, **feedback buttons** (thumbs/save/dismiss/applied),
  **profile editor**.
- **Chrome extension** — content badge with match score; popup with score
  breakdown + "save to OpportunityPulse".

UX principles: simple, fast first value, explainable, never noisy.

---

## 9. API design

Full list in [`docs/api.md`](docs/api.md). FastAPI, REST + a little RPC, JWT/
OAuth, rate-limited, OpenAPI auto-docs:

```
POST   /profiles                       create profile
PATCH  /profiles/{id}                  edit profile
POST   /profiles/{id}/resume           upload + parse résumé
GET    /opportunities                  search: q, intent, filters, sort, page
GET    /opportunities/{id}             detail
GET    /opportunities/{id}/explanation ranking explanation
GET    /clusters/{id}                  dedup cluster view
POST   /deadlines/extract              ad hoc deadline extraction
POST   /opportunities/{id}/outreach    type-routed outreach artifact
POST   /feedback                       submit feedback signal
GET    /alerts  POST /alerts  PATCH /alerts/{id}
GET    /sources POST /sources PATCH /sources/{key}   (admin)
GET    /admin/health                   pipeline + source health + eval dashboards
```

---

## 10. Evaluation & metrics

See [`docs/evaluation.md`](docs/evaluation.md).

- **Offline.** Retrieval: Recall@k, MRR, nDCG on a hand-labeled set. Rerank:
  nDCG lift. Dedup: pairwise P/R/F1 + cluster purity. Deadline: exact-match,
  ±-day tolerance, relative-phrase recall, review-queue rate. Outreach: LLM-judge
  + human rubric.
- **Online.** CTR, save-rate, dismiss-rate, apply-rate, alert open-rate, latency
  p50/p95, freshness lag, pipeline job success rate, alert timeliness.
- **Manual review.** Weekly samples of low-confidence deadlines, borderline
  dedup pairs, and outreach drafts. Tracked in LangSmith + the `evaluation/`
  harness with versioned datasets.

---

## 11. Tech stack & rationale

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | async-native, typed, free OpenAPI docs |
| DB + vectors | PostgreSQL + pgvector | one store for relational + vectors; simpler cloud ops than a separate FAISS service (FAISS kept as optional local fast path) |
| Cache/queue | Redis | Arq backend + caches |
| Workers | Arq | lightweight, async-native (Celery swap documented) |
| Orchestration | LangGraph | stateful, branching, retryable, HITL graphs |
| LLM glue | LangChain (narrow) | loaders/splitters/retriever/LLM abstraction only |
| Embeddings | sentence-transformers (`bge-small`) | free, offline, reproducible; hosted swap available |
| Rerank | cross-encoder MiniLM | precision second stage |
| Discovery | Tavily (default) / SerpAPI | web discovery + query expansion |
| Scraping | Playwright | last resort for JS-heavy pages |
| LLMs | Claude (default) / OpenAI / Ollama | provider-agnostic; local = zero-cost fallback |
| Web | Next.js | SSR/CSR, App Router |
| Extension | Chrome MV3 | in-page match score |
| Observability | LangSmith + OTel/Prometheus + logs | agent traces + metrics |
| Ops | Docker + GitHub Actions | parity + CI/deploy to Fly.io |
| Data | Kaggle API, GitHub token | competition source + eval datasets; OSS source + CI |

---

## 12. Implementation roadmap

Per-phase goals/tasks/deliverables/dependencies/complexity/demo in
[`docs/roadmap.md`](docs/roadmap.md):

- **Phase 0 — Setup:** monorepo, docker-compose, env, CI skeleton, base schema +
  migrations. *Demo:* `docker compose up` healthchecks.
- **Phase 1 — MVP:** profile + 5–8 API/ATS sources + normalize + bi-encoder
  match + feed + basic deadlines + explanation chips. *Demo:* ranked feed.
- **Phase 2 — Ranking + dedup:** clustering, cross-encoder rerank, score blend +
  explanation panel. *Demo:* "also seen on" + why-matched.
- **Phase 3 — Deadline intelligence + reminders:** fuzzy NLP ladder + review
  queue + decay + alerts + calendar export. *Demo:* urgency tracker.
- **Phase 4 — Outreach agent:** type-routed RAG generator + HITL. *Demo:* cold
  email for a lab vs cover letter for a job.
- **Phase 5 — Chrome extension:** content badge + popup. *Demo:* live score on a
  listing page.
- **Phase 6 — Learning loop + observability:** feedback weights, LangSmith, eval
  harness. *Demo:* metrics dashboard + ranking improving with feedback.
- **Phase 7 — Production hardening:** auth, rate limits, source-health
  auto-disable, backups, deploy workflow, latency tuning. *Demo:* live URL.

---

## 13. Repository structure

See [`CLAUDE.md`](CLAUDE.md#repository-layout) for the annotated tree. Monorepo
with `backend/ worker/ agents/ ingestion/ ranking/ dedup/ deadline_parser/
email_agent/ models/ evaluation/ web/ extension/ infra/ scripts/ tests/ docs/`.

---

## 14. Interview framing

Full scripts + hard-question answers in [`docs/interview.md`](docs/interview.md).
Tailored angles: **Info Edge** (semantic discovery layer over a Naukri-like
corpus: dedup, ranking, freshness); **Fidelity** (ML fundamentals,
retrieval+rerank, evaluation rigor, end-to-end ownership); **DTDC** (pipeline /
operational thinking, timelines, urgency/decay, reliability + monitoring).

---

## 15. Practical constraints & tradeoffs

Solo-buildable and phase-gated; structured endpoints preferred over scraping;
one Postgres for relational+vector to cut ops; Arq over Celery for lighter
async; local embeddings to keep cost near zero with a hosted swap available;
draft-only outreach to avoid ToS/abuse risk; every ML stage has a deterministic
fallback; source-health auto-disable for resilience; human review on
low-confidence deadlines, borderline dedup, and all outreach drafts. Tradeoffs
are made explicit so the system can grow without rewrites.
