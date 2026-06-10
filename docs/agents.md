# Agent orchestration (LangGraph)

All multi-step, stateful, retryable, or human-in-the-loop work is a LangGraph
graph in [`agents/graphs/`](../agents/graphs/). Graphs share a typed
`GraphState` ([`agents/state.py`](../agents/state.py)) and a provider-agnostic
LLM layer ([`agents/llm.py`](../agents/llm.py)).

## Why LangGraph (and where LangChain stops)

LangGraph gives explicit nodes/edges, conditional branching, per-node retries,
checkpointing, and interrupt points for human approval — exactly what these
pipelines need. LangChain is used **only** for document loaders, text splitters,
retriever wrappers, and as a thin LLM/provider abstraction. The ranking math,
dedup, and deadline rules stay as plain, unit-testable Python so they are
debuggable and have deterministic fallbacks.

---

## 1. Profile ingestion

```
receive ──> parse_resume ──> extract_skills ──> build_intents ──> embed ──> persist
                  │
                  └─(parse fail)─> form_only_path ──> build_intents
```

- **Branching:** résumé parse failure → form-only path.
- **Retries:** parse ×2 with backoff.
- **Caching:** embeddings keyed by profile content hash.
- **HITL:** optional review of parsed skills (off by default).
- **Failure:** if embedding fails, persist profile with lexical fallback flag.

## 2. Discovery

```
select_sources ──> [fan-out per adapter] ──> fetch ──> parse ──> emit_raw ──> normalize
```

- **Branching:** per-adapter method follows the source's `access_method` ladder.
- **Retries:** fetch retried with exponential backoff + jitter.
- **Failure isolation:** one adapter failing does not stop others; it updates
  `opportunity_sources.health_json` and may auto-disable the source.
- **Caching:** ETag / If-Modified-Since + content fingerprint.
- **HITL:** none (admin can review source health).

## 3. Dedup + ranking

```
load_new ─> block ─> pairwise_sim ─> cluster ─> merge ─> embed_canonical
        ─> retrieve ─> rerank ─> score ─> explain ─> persist
                          │
                          └─(over latency budget)─> skip rerank
```

- **Branching:** reranker skipped when over budget.
- **Caching:** canonical embeddings; retrieval results per (user, intent).
- **Failure:** embedding/index failure → lexical retrieval fallback.

## 4. Deadline update

```
collect_text ─> rules ─(conf<θ)─> ner ─(conf<θ)─> llm ─> confidence ─> persist
                                                            │
                                                            └─(conf<θ)─> review_queue
```

- **HITL:** the review queue (low-confidence deadlines) is surfaced to admins.
- **Retries:** LLM ×2 → fall back to best lower-rung result or `unknown`.

## 5. Outreach generation (on-demand)

```
route_by_type ─> retrieve_context (RAG) ─> draft ─> self_check ─> present_for_approval
```

- **route_by_type:** maps `listing.type` → artifact type (cold email only for
  research/lab; see [`ml-design.md`](ml-design.md#9-outreach-generation-rag-type-routed)).
- **self_check:** verifies claims are grounded in retrieved context.
- **HITL gate:** `present_for_approval` interrupts the graph; nothing is saved as
  `approved` or ever sent without explicit user action.
- **Caching:** RAG context cached per listing.
- **Failure:** thin RAG → labeled template draft with low-grounding flag.

## 6. Feedback learning

```
collect_signals ─> update_weights(online) ─(threshold)─> schedule_offline_retrain
```

- **Failure:** keep prior weights; never degrade ranking on a bad update.
- **Guardrail:** exploration term prevents filter-bubble collapse.

## 7. Notification

```
eval_rules ─> dedupe_alerts ─> schedule ─> dispatch ─> record
                                              │
                                              └─(fail ×3)─> inapp_fallback
```

- **Retries:** dispatch ×3; then fall back to in-app notification.
- **De-dup:** suppress repeat alerts for the same (user, listing, rule).

---

## Cross-cutting

- **Tracing:** every graph run is traced in LangSmith (node timings, token use,
  retries).
- **Idempotency:** discovery/dedup jobs keyed by content fingerprint so re-runs
  are safe.
- **Provider abstraction:** `agents/llm.py` exposes `complete()` / `embed()`
  over Claude (default), OpenAI, and Ollama (local fallback), selected by env.
