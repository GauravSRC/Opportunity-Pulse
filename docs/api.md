# API design

FastAPI, REST + a little RPC. JWT/OAuth auth, per-user rate limiting, OpenAPI
docs at `/docs`. Routers live in [`backend/app/api/`](../backend/app/api/).

## Conventions

- JSON in/out; Pydantic schemas in [`backend/app/schemas/`](../backend/app/schemas/).
- Cursor or page/limit pagination on list endpoints.
- Errors: RFC-7807-style `{type, title, detail, status}`.
- All mutating endpoints are idempotent where feasible (client-supplied keys).

## Endpoints

### Profiles
| Method | Path | Body / Query | Returns |
|---|---|---|---|
| POST | `/profiles` | profile create | profile |
| PATCH | `/profiles/{id}` | partial update | profile |
| POST | `/profiles/{id}/resume` | multipart file | parse status + extracted profile |
| GET | `/profiles/{id}` | — | profile |

### Opportunities
| Method | Path | Query | Returns |
|---|---|---|---|
| GET | `/opportunities` | `q, intent, type, location, remote, deadline_before, sort, page, limit` | ranked page |
| GET | `/opportunities/{id}` | — | listing detail (+ canonical cluster) |
| GET | `/opportunities/{id}/explanation` | `user_id` | `components_json` breakdown + matched skills |

### Dedup
| GET | `/clusters/{id}` | — | cluster members + merged metadata |

### Deadlines
| POST | `/deadlines/extract` | `{text}` | `{kind, resolved_date?, anchor_text?, confidence, extractor}` |

### Outreach (type-routed)
| POST | `/opportunities/{id}/outreach` | `{user_id, tone?, regenerate?}` | `{artifact_type, subject?, body, rag_sources}` |

> The response `artifact_type` is decided server-side by the router from
> `listing.type` — **cold_email only for research/lab**, otherwise cover_letter
> / sop / team_pitch / proposal / referral_note. The client renders whatever
> type comes back; it must not assume "cold email".

| PATCH | `/outreach/{id}` | `{body, status}` | updated artifact (status: draft/approved/discarded — never sent) |

### Feedback
| POST | `/feedback` | `{user_id, listing_id, signal, context}` | ack |

### Alerts
| GET | `/alerts` | — | list |
| POST | `/alerts` | `{rule, channel}` | alert subscription |
| PATCH | `/alerts/{id}` | `{enabled, channel}` | updated |

### Sources (admin)
| GET | `/sources` | — | source list + health |
| POST | `/sources` | source config | created |
| PATCH | `/sources/{key}` | `{enabled, config}` | updated |

### Admin / monitoring
| GET | `/admin/health` | — | pipeline status, source health, eval snapshot |
| GET | `/healthz` | — | liveness |
| GET | `/readyz` | — | readiness (db + redis) |

## Example: outreach response

```json
{
  "artifact_type": "cold_email",
  "subject": "Prospective summer research in your vision lab",
  "body": "Dear Prof. ...",
  "rag_sources": [
    {"kind": "lab_page", "url": "https://.../lab"},
    {"kind": "paper", "url": "https://arxiv.org/abs/..."}
  ],
  "status": "draft",
  "grounding": "high"
}
```

For a company internship the same endpoint returns
`"artifact_type": "cover_letter"` with no `subject`, demonstrating the routing.
