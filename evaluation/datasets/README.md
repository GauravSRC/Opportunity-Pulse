# Evaluation datasets

Versioned, hand-labeled datasets for offline evaluation. Keep them small,
documented, and version-suffixed (`*_v1.jsonl`). Reports are written to
`../reports/` (gitignored).

| File | Used by | Schema (one JSON object per line) |
|---|---|---|
| `retrieval_v1.jsonl` | `retrieval_eval` | `{"profile": {...}, "relevant_listing_ids": [...]}` |
| `dedup_v1.jsonl` | `dedup_eval` | `{"a": {...}, "b": {...}, "is_duplicate": true}` |
| `deadline_v1.jsonl` | `deadline_eval` | `{"text": "...", "expected_kind": "...", "expected_date": "YYYY-MM-DD"\|null, "anchor": null}` |
| `outreach_v1.jsonl` | `email_eval` | `{"listing": {...}, "profile": {...}}` |

TODO(phase-6): seed each dataset with ~50–100 carefully labeled examples,
including hard relative-deadline phrases ("two weeks before demo day",
"rolling until filled").
