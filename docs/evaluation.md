# Evaluation & metrics

Three tiers: **offline** (versioned datasets), **online** (production signals),
and **manual review** (weekly human sampling). The harness lives in
[`evaluation/`](../evaluation/); runs are tracked in LangSmith.

## Offline metrics

| Component | Metrics | Dataset |
|---|---|---|
| Retrieval | Recall@k, MRR, nDCG | hand-labeled (profile, relevant-listing) pairs |
| Reranker | nDCG lift vs retrieval-only | same, with rerank applied |
| Dedup | pairwise Precision/Recall/F1, cluster purity | labeled duplicate/non-duplicate pairs |
| Deadline | exact-match acc, ±N-day tolerance acc, relative-phrase recall, review-queue rate | annotated deadline phrases |
| Outreach | LLM-judge rubric (relevance, grounding, tone, specificity) | curated listing+profile pairs |

Datasets are versioned under [`evaluation/datasets/`](../evaluation/datasets/);
each eval script writes a JSON report and a markdown summary.

## Online metrics

| Area | Metric |
|---|---|
| Engagement | CTR, save-rate, dismiss-rate, apply-rate |
| Alerts | open-rate, timeliness (alert sent vs. deadline) |
| Latency | p50 / p95 for search, detail, outreach |
| Freshness | lag between source publish and feed appearance |
| Reliability | pipeline job success rate, adapter error rate |

## Manual review (weekly)

- Sample of **low-confidence deadlines** (`needs_review = true`).
- Sample of **borderline dedup pairs** (score near threshold).
- Sample of **outreach drafts** for grounding/tone before they reach users at
  scale.

## Harness commands (later phases)

```bash
python -m evaluation.harness --all
python -m evaluation.retrieval_eval --dataset datasets/retrieval_v1.jsonl
python -m evaluation.dedup_eval --dataset datasets/dedup_v1.jsonl
python -m evaluation.deadline_eval --dataset datasets/deadline_v1.jsonl
python -m evaluation.email_eval --judge claude
```

## Acceptance gates (initial targets, tune with data)

- Retrieval Recall@20 ≥ 0.85 on the labeled set.
- Dedup F1 ≥ 0.90; cluster purity ≥ 0.95.
- Deadline exact-or-±3-day accuracy ≥ 0.80; review-queue rate ≤ 0.15.
- Outreach grounding "high" ≥ 0.90 of sampled drafts (no invented facts).
- p95 search latency ≤ 400 ms (reads precomputed scores).
