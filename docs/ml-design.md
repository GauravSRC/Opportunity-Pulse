# ML / AI design

Each component lists a **baseline** (ship first, no surprises) and an
**advanced** variant, plus its **deterministic fallback** and **evaluation**.

## 1. Profile embedding

- **Input → text:** structured profile rendered through a template into a natural
  language document (headline, top skills, intents, notable projects).
- **Multi-intent:** one vector per declared intent (`research`, `job`, ...),
  stored in `embeddings` with `intent` set. Retrieval uses the vector matching
  the active query intent.
- **Model:** default `BAAI/bge-small-en-v1.5` (384-d, fast). Swap to
  `all-mpnet-base-v2` or a hosted embedding API via `EMBEDDING_MODEL` /
  `EMBEDDING_PROVIDER` env.
- **Fallback:** if embedding fails, fall back to a lexical profile (skill token
  set) used with BM25.
- **Eval:** retrieval metrics below; ablation of single- vs multi-intent.

## 2. Opportunity embedding

- **Input → text:** `title + org + type + skills + summary`, same model/space as
  profiles.
- **Storage:** pgvector with an HNSW index (`vector_cosine_ops`).
- **Refresh:** recomputed on canonical-record merge (post-dedup).

## 3. Retrieval (bi-encoder)

- **Baseline:** cosine top-K via pgvector + a BM25 lexical channel; combine with
  a simple weighted sum.
- **Advanced:** multi-intent retrieval + **reciprocal-rank fusion** of dense and
  lexical result lists.
- **Fallback:** lexical-only when the vector index is unavailable.
- **Eval:** Recall@k, MRR, nDCG on a hand-labeled (profile, relevant-listing) set.

## 4. Cross-encoder reranker (optional second stage)

- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` over the top-K from retrieval.
- **Gating:** skipped when the per-request latency budget is exceeded (graph
  branch); retrieval order is then used directly.
- **Eval:** nDCG lift vs. retrieval-only.

## 5. Query expansion

- LLM expands sparse intents into a richer skill/term set, used for both
  retrieval and discovery search queries (Tavily/SerpAPI).
- **Fallback:** static synonym map from `skills.aliases` when the LLM is
  unavailable.

## 6. Deduplication

- **Blocking:** canonical-URL equality + normalized (title, org) buckets to
  generate candidate pairs cheaply.
- **Scoring:** embedding cosine + `rapidfuzz` token-set ratio on title/org.
- **Clustering:** threshold the combined score → **union-find** clusters.
- **Merge:** choose richest fields, union skills, earliest `posted_at`, keep all
  source URLs in `merged_metadata_json`; mark one member `is_canonical`.
- **Fallback:** exact URL + exact normalized-title match only.
- **Eval:** pairwise Precision/Recall/F1 and cluster purity on a labeled set;
  weekly manual review of borderline pairs.

## 7. Deadline extraction (fallback ladder)

```
text → (1) rules (dateparser + regex) → conf?
            ↓ low
       (2) spaCy NER / pattern matcher → conf?
            ↓ low
       (3) LLM fallback (structured extraction) → conf?
            ↓ low
       needs_review = true  (human queue)
```

- **Rules:** absolute dates; common relative ("within 7 days", "end of
  quarter"); "rolling until filled"/"until positions filled" → `kind=rolling`.
- **NER:** date entities + nearby anchor nouns.
- **LLM:** fuzzy/anchored phrases ("two weeks before demo day") → emit
  `{kind, resolved_date?, anchor_text, raw_phrase, confidence}`. If anchored to
  an unknown event, store `anchor_text` and leave `resolved_date` null
  (`needs_anchor`).
- **Fallback:** if the LLM is down, stop at the best rules/NER result (or
  `unknown`). The product never blocks on the LLM.
- **Eval:** exact-match accuracy, ±N-day tolerance accuracy, relative-phrase
  recall, and review-queue rate (lower is better, but precision-protected).

## 8. Decay / urgency model

- **Baseline:** urgency = f(`time_to_deadline`, `posting_age`,
  `source_velocity`) via exponential decay; `rolling` deadlines get a slow,
  bounded decay; `unknown` gets a neutral prior.
- **Advanced:** logistic regression / survival model trained on observed "was it
  still open at time t?" labels harvested as listings age out.
- **Use:** feeds the ranking `urgency` component and alert rules.

## 9. Outreach generation (RAG, type-routed)

The router ([`email_agent/router.py`](../email_agent/router.py)) selects the
artifact from `listing.type` — this is the core product rule:

| listing.type | artifact_type | RAG context |
|---|---|---|
| research | **cold_email** | lab page + recent papers (arXiv/OpenAlex) + user projects |
| internship/job | cover_letter / referral_note | company page + JD + user experience |
| fellowship/grant | sop / proposal | program page + eligibility + user goals |
| hackathon | team_pitch | event page + theme + user skills |
| gsoc | proposal + mentor_intro | org/project page + idea list + user OSS history |
| conference | submission / travel_grant_note | CFP + user research |

- **Pipeline:** `route_by_type → retrieve_context(RAG) → draft → self_check →
  present_for_approval`. Self-check verifies claims are grounded in retrieved
  context (no invented publications). **HITL gate**; never auto-sent.
- **Fallback:** if RAG retrieval is thin, generate a clearly-labeled
  template-based draft and flag low grounding.
- **Eval:** LLM-judge rubric (relevance, grounding, tone, specificity) + weekly
  human review.

## 10. Feedback-based ranking

- **Signals:** implicit (click/save/dismiss/apply) + explicit (thumbs).
- **Online:** per-user logistic-regression / bandit update on the score-blend
  coefficients `{semantic, skill_overlap, recency, urgency}` with an exploration
  term to avoid filter-bubble collapse.
- **Offline:** periodic retrain from the feedback log; versioned by
  `model_version`.
- **Fallback:** keep prior weights if an update/retrain fails.

## Final score blend (explainable)

```
score = w_sem*semantic + w_skill*skill_overlap + w_rec*recency + w_urg*urgency
        (+ w_fb*feedback_prior)
```

`components_json` stores each weighted contribution so the "Why it matched"
panel and the extension can render the breakdown verbatim. See
[`ranking/scorer.py`](../ranking/scorer.py) and
[`ranking/explain.py`](../ranking/explain.py).

## Model registry

Model ids, dims, and versions are documented in [`../models/README.md`](../models/README.md)
and selected via environment variables so every choice is swappable without code
changes.
