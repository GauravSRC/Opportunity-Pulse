# Data model

PostgreSQL + the `pgvector` extension. Every table has `id UUID PRIMARY KEY
DEFAULT gen_random_uuid()`, `created_at TIMESTAMPTZ`, `updated_at TIMESTAMPTZ`.
Enums are implemented as Postgres `ENUM` types (or `TEXT` + check constraints in
SQLite test mode). The SQLAlchemy mapping lives in
[`backend/app/models/`](../backend/app/models/); the initial migration in
[`backend/alembic/`](../backend/alembic/).

## Entity overview

```
users ─┬─< user_profiles >─── skills (via profile_skills)
       └─< feedback >── normalized_listings ──< deadlines
                              │      │
opportunity_sources ──< raw_listings   └──< rank_scores >── users
                              │
                       dedup_clusters (canonical_listing_id -> normalized_listings)
normalized_listings ──< outreach_artifacts >── users
users ──< alerts >── normalized_listings
embeddings (polymorphic) ; audit_logs (polymorphic)
```

## Tables & key fields

### users
| field | type | notes |
|---|---|---|
| email | citext unique | login id |
| auth_provider | enum(local,google,github) | |
| hashed_pw | text null | local auth |
| oauth_sub | text null | external subject |
| role | enum(user,admin) | |
| settings_json | jsonb | notification prefs, channels, timezone |

### skills
| field | type | notes |
|---|---|---|
| canonical_name | text unique | e.g. "PyTorch" |
| aliases | text[] | "torch", "py-torch" |
| category | text | language/framework/domain |
| embedding_id | uuid fk embeddings | for skill-level similarity |

### user_profiles
| field | type | notes |
|---|---|---|
| user_id | uuid fk users | |
| headline | text | |
| education_json | jsonb | degrees, institutions, years |
| experience_json | jsonb | roles, projects |
| intents | enum[] | research, internship, job, fellowship, hackathon, grant |
| locations | text[] | preferred locations |
| is_remote_ok | bool | |
| resume_blob_ref | text null | object-store key (encrypted) |
| preferences_json | jsonb | filters, weighting hints |

`profile_skills` join: (profile_id, skill_id, proficiency).

### opportunity_sources
| field | type | notes |
|---|---|---|
| key | text unique | matches `registry.yaml` key |
| name | text | |
| category | text | jobs/research/grant/hackathon/... |
| access_method | enum(api,ats_json,rss,sitemap,search,browser) | drives the fallback ladder |
| base_url | text | |
| config_json | jsonb | per-source params (org slug, query, selectors) |
| enabled | bool | |
| health_json | jsonb | success_rate, parse_error_rate, freshness_lag |
| last_run_at | timestamptz | |

### raw_listings
| field | type | notes |
|---|---|---|
| source_id | uuid fk | |
| external_id | text | source's id (for idempotency) |
| url | text | |
| fetched_at | timestamptz | |
| payload_json | jsonb | raw fetched record |
| content_fingerprint | text | sha256 of normalized payload (dedupe re-fetch) |
| status | enum(new,normalized,error) | |

Unique: (source_id, external_id).

### normalized_listings
| field | type | notes |
|---|---|---|
| raw_id | uuid fk raw_listings | |
| source_id | uuid fk | |
| title | text | |
| org | text | company/lab/university |
| type | enum(job,internship,research,fellowship,hackathon,grant,conference,gsoc) | drives outreach routing |
| location | text null | |
| is_remote | bool | |
| url | text | canonical URL |
| posted_at | timestamptz null | |
| description | text | cleaned body |
| skills | text[] | extracted skill tokens |
| links_json | jsonb | {lab_page, paper_urls[], apply_url, contact_email?} |
| cluster_id | uuid fk dedup_clusters null | set after dedup |
| is_canonical | bool | true for the cluster's representative |

### deadlines
| field | type | notes |
|---|---|---|
| listing_id | uuid fk normalized_listings | |
| kind | enum(fixed,rolling,relative,unknown) | |
| resolved_date | timestamptz null | null when rolling/unknown/unresolved relative |
| anchor_text | text null | e.g. "demo day" for relative phrases |
| raw_phrase | text | source phrase ("rolling until filled") |
| confidence | float | 0..1 |
| needs_review | bool | true when confidence < threshold |
| extractor | enum(rule,ner,llm) | which ladder rung produced it |

### rank_scores
| field | type | notes |
|---|---|---|
| user_id | uuid fk | |
| listing_id | uuid fk | |
| score | float | final blended score |
| components_json | jsonb | {semantic, skill_overlap, recency, urgency, feedback} |
| model_version | text | for reproducibility |
| computed_at | timestamptz | |

Unique: (user_id, listing_id, model_version).

### dedup_clusters
| field | type | notes |
|---|---|---|
| canonical_listing_id | uuid fk normalized_listings | representative |
| member_ids | uuid[] | all listings in the cluster |
| method_json | jsonb | {url_match, cosine, fuzzy_score, threshold} |
| confidence | float | |
| merged_metadata_json | jsonb | union of skills, earliest posted_at, all source URLs |

### outreach_artifacts
| field | type | notes |
|---|---|---|
| user_id | uuid fk | |
| listing_id | uuid fk | |
| artifact_type | enum(cold_email,cover_letter,sop,team_pitch,proposal,referral_note) | chosen by router from listing.type |
| rag_sources_json | jsonb | provenance: lab page, papers, profile snippets used |
| subject | text null | emails only |
| body | text | editable draft |
| status | enum(draft,approved,discarded) | never auto-sent |
| model_version | text | |

### feedback
| field | type | notes |
|---|---|---|
| user_id | uuid fk | |
| listing_id | uuid fk | |
| signal | enum(click,save,dismiss,thumbs_up,thumbs_down,applied) | |
| weight | float | implicit vs explicit weighting |
| context_json | jsonb | rank position, query, surface |

### alerts
| field | type | notes |
|---|---|---|
| user_id | uuid fk | |
| listing_id | uuid fk | |
| rule | text | e.g. "high_fit_closing_soon" |
| channel | enum(inapp,email,calendar) | |
| scheduled_for | timestamptz | |
| sent_at | timestamptz null | |
| status | enum(pending,sent,failed,suppressed) | |

### embeddings
| field | type | notes |
|---|---|---|
| owner_type | enum(profile,listing,skill) | polymorphic |
| owner_id | uuid | |
| intent | text null | for multi-intent profile vectors |
| model | text | e.g. bge-small-en-v1.5 |
| dim | int | |
| vector | vector(dim) | pgvector; HNSW index |

Index: `CREATE INDEX ON embeddings USING hnsw (vector vector_cosine_ops);`

### audit_logs
| field | type | notes |
|---|---|---|
| actor | text | user id or "system:<agent>" |
| action | text | |
| entity | text | table name |
| entity_id | uuid null | |
| meta_json | jsonb | |
| ts | timestamptz | |

## Notes

- **Provenance everywhere:** raw → normalized → cluster chains preserve where a
  listing came from and when, satisfying the sourcing ethics requirements.
- **Idempotency:** (source_id, external_id) + content_fingerprint prevent
  duplicate ingestion on re-fetch.
- **Multi-intent vectors:** the `embeddings.intent` column lets one profile hold
  several vectors (research vs job) for intent-aware retrieval.
