# Interview framing

Honest, specific, no overclaiming. Lead with the problem and the engineering
decisions, not the buzzwords.

## 30-second pitch

> OpportunityPulse is a semantic discovery platform that continuously pulls
> jobs, research roles, fellowships, hackathons, and grants from 30+ sources,
> deduplicates the same listing across sites, reads messy deadlines out of free
> text, and ranks everything against your profile with an explainable score. For
> each opportunity it drafts the *right* outreach — a cold email for a
> professor's lab, a cover letter for a company job — always for you to review,
> never auto-sent.

## 2-minute explanation

> Students lose hours every week hunting across dozens of sites. The same job
> shows up five times, deadlines are buried in prose like "rolling until
> filled," and writing outreach from scratch is exhausting.
>
> I built a multi-agent pipeline. Discovery adapters — one thin adapter per
> source, preferring official APIs and ATS JSON over scraping — pull listings
> and normalize them into one schema. A dedup stage blocks candidates, then
> combines embedding similarity with fuzzy string matching and union-find
> clustering to merge duplicates. A deadline stage runs a fallback ladder:
> deterministic rules first, then NER, then an LLM for fuzzy phrases, each with a
> confidence score and a human-review queue below threshold. Ranking is a
> bi-encoder retrieval over pgvector with an optional cross-encoder reranker,
> then a transparent weighted blend of semantic similarity, skill overlap,
> recency, and urgency — and I store every component so the UI can show *why*
> something matched. Outreach is type-routed with RAG: the artifact depends on
> the opportunity type, and it's always human-approved.
>
> The whole thing is orchestrated with LangGraph for the stateful, retryable,
> human-in-the-loop flows, with deterministic fallbacks at every ML stage so a
> model outage degrades gracefully instead of 500-ing. It's evaluated offline
> (Recall@k, dedup F1, deadline accuracy), online (CTR, latency, freshness), and
> with weekly manual review.

## Tailored talking points

**Info Edge (Naukri).** This is a modern semantic discovery layer over a
job-corpus: cross-source dedup, intent-aware ranking, freshness/recency modeling,
and explainability — directly analogous to improving relevance and de-duplication
on a large listings marketplace.

**Fidelity.** Demonstrates ML fundamentals end to end: embeddings, retrieval,
reranking, a transparent scoring function, an evaluation harness with offline +
online + human tiers, and decision support (urgency/decay). Emphasize ownership,
rigor, and graceful degradation.

**DTDC.** Pipeline and operational thinking: scheduled ingestion with rate
limiting and backoff, idempotency by fingerprint, source-health monitoring with
auto-disable, deadline/timeline modeling, alert timeliness, and reliability
metrics — operational decision support, not just a model.

## Hardest questions + crisp answers

**"How do you know dedup is correct?"** Labeled pairwise dataset → Precision/
Recall/F1 + cluster purity; a tunable threshold; and weekly manual review of
borderline pairs. Blocking keeps it cheap; the fallback is exact URL+title match
so we never over-merge silently.

**"What if the LLM hallucinates a deadline?"** The LLM is the *last* rung, only
reached when rules and NER are low-confidence, and its output carries a
confidence score. Below threshold it goes to a human-review queue rather than to
the user. We also store the raw phrase so reviewers see the evidence.

**"Cold-start ranking for a brand-new user?"** Multi-intent profile embedding
gives immediate semantic relevance with zero feedback; skill overlap and recency
fill the gap; feedback weights only refine from there, with an exploration term
so we don't collapse onto early signals.

**"Isn't scraping legally risky?"** That's why the ladder prefers official APIs
and ATS JSON, honors robots.txt and ToS, never touches login-walled or paid
data, and reserves Playwright for JS-only public pages. Provenance is stored for
every listing. Outreach is never auto-sent.

**"Cross-encoder latency?"** It's a second stage over only the top-K, and it's
latency-gated — the graph skips it when over budget and serves the bi-encoder
order. Reads hit precomputed scores, so user-facing p95 stays low.

**"How do you avoid a feedback filter bubble?"** Online updates include an
exploration term; offline retrains are versioned and evaluated before promotion;
recency and urgency components keep fresh items visible regardless of past
clicks.

**"What breaks when a source changes its HTML?"** Adapters are schema-tolerant
and isolated; one failing source doesn't stop the pipeline. The health monitor
detects rising parse-error rate and auto-disables the source while raising an
alert, and we can fail over to the next rung of the ladder (e.g., RSS → sitemap).

## What I'd say honestly about limitations

Coverage is breadth-vs-reliability: I prioritized sources with structured
endpoints. Deadline extraction on truly ambiguous phrases still needs human
review. The decay model starts heuristic until enough "still open?" labels
accumulate. These are deliberate, staged tradeoffs — documented, not hidden.
