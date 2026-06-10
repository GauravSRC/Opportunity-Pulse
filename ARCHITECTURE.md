# Architecture

A system map for OpportunityPulse. For the narrative end-to-end design see
[`PROJECT.md`](PROJECT.md); for module-level detail see [`docs/`](docs/).

## High-level diagram

```
                     ┌──────────────┐      ┌────────────────────┐
  Browser/Extension ─▶│  Next.js Web │────▶│  FastAPI (sync API) │
                     └──────────────┘      │  read / search /    │
                                           │  draft / feedback   │
                                           └─────────┬───────────┘
                                                     │ enqueue jobs
                                           ┌─────────▼───────────┐
                                           │  Redis queue + cache │
                                           └─────────┬───────────┘
                                                     │
   ┌──────────────────────── Worker pipeline (async, Arq) ─────────────────────┐
   │  Discovery → Normalize → Dedup → Deadline → Ranking → Decay → Alerts       │
   │  Feedback (offline)            Outreach (on-demand, human-in-the-loop)     │
   │  — each orchestrated as a LangGraph graph (agents/graphs/)                 │
   └────────────┬───────────────────────┬───────────────────────┬──────────────┘
                │                        │                       │
        ┌───────▼────────┐      ┌────────▼────────┐     ┌────────▼─────────┐
        │  PostgreSQL     │      │   pgvector       │     │  LangSmith +      │
        │  (relational    │      │   (embeddings,   │     │  OTel/Prometheus  │
        │   state)        │      │   HNSW index)    │     │  + structured logs│
        └─────────────────┘      └──────────────────┘     └───────────────────┘
```

## Sync vs async boundary

| Path | Mode | Why |
|---|---|---|
| Search, opportunity detail, explanation, feed | **Sync** (FastAPI) | User waits; reads precomputed rank scores from Postgres. |
| Outreach draft on demand | **Sync request, async-capable** | RAG + LLM; streamed; cached per listing. HITL gate. |
| Discovery, normalize, dedup, embedding, batch ranking, decay, alert dispatch | **Async** (Arq workers) | Long-running, scheduled, retryable, fan-out. |
| Feedback weight updates | **Async** | Cheap online update + scheduled offline retrain. |

## Component responsibilities

- **Web (Next.js):** onboarding, feed, detail + "why it matched", deadline
  tracker, outreach panel (type-routed), settings, feedback controls.
- **Extension (MV3):** content-script match badge + popup score breakdown.
- **FastAPI backend:** auth, REST endpoints, read models, enqueue jobs,
  on-demand outreach, OpenAPI docs.
- **Arq workers:** run the LangGraph pipelines on schedule and on demand.
- **agents/:** LangGraph graphs (discovery, dedup_rank, deadline, outreach,
  feedback, notification), shared `GraphState`, provider-agnostic `llm.py`.
- **ingestion/:** one adapter per source type, registry, rate limiter, robots
  checker, source-health monitor, normalizer.
- **ranking/ dedup/ deadline_parser/ email_agent/:** the ML/algorithmic cores,
  each plain testable Python with deterministic fallbacks.
- **Postgres + pgvector:** single store for relational state and vectors.
- **Redis:** Arq job queue + caches (ETag/fingerprint, RAG context, embeddings).
- **Observability:** LangSmith traces for agent runs; Prometheus/OTel metrics;
  structured JSON logs.

## Data flow (new opportunity → ranked feed)

1. **Discovery graph** selects enabled sources, fans out to adapters, fetches
   (conditional GET / rate-limited), parses, emits `raw_listings`, normalizes to
   `normalized_listings`.
2. **Dedup+rank graph** blocks candidates, computes pairwise similarity
   (embedding cosine + fuzzy title/org), clusters (union-find), merges to a
   canonical record, embeds it, retrieves top-K per user intent vector,
   optionally cross-encoder reranks, blends component scores, writes
   `rank_scores` + explanation.
3. **Deadline graph** runs the rules→NER→LLM ladder, writes `deadlines` with
   confidence; low confidence → review queue.
4. **Decay** recomputes urgency; **Alert graph** fires rules.
5. User opens the **feed** (sync) → reads precomputed scores + explanations.
6. On a listing, user requests **outreach** → router picks the artifact type →
   RAG → draft → HITL approval.

## Failure & resilience

- Per-adapter isolation: one source failing does not stop others; the
  source-health monitor auto-disables a flapping source and raises an alert.
- LLM/embedding failures fall back to deterministic paths (lexical search,
  rules-only deadlines, prior ranking weights).
- Retries with backoff on fetch/LLM/dispatch; idempotent jobs keyed by content
  fingerprint.

## Deployment

Dockerized services; managed Postgres+pgvector and Redis; deploy via GitHub
Actions to a Fly.io/Render/Railway-class host. See
[`infra/`](infra/) and `.github/workflows/deploy.yml`.
