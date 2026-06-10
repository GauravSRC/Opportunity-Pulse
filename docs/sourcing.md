# Data sourcing strategy

## Principle

Prefer structured, ToS-friendly endpoints. Scrape only as a last resort. Always
check `robots.txt` and the source's Terms of Service, identify the crawler,
respect rate limits, and cache aggressively. **No Reddit API** and no
login-walled or paid-data scraping.

## Per-source fallback ladder

```
Official API  →  ATS JSON  →  RSS/Atom  →  sitemap.xml  →  search API  →  Playwright (last resort)
```

An adapter declares its preferred method in `registry.yaml`; if a method breaks,
the source-health monitor flags it and we can fail over to the next rung.

## 30+ source categories

| # | Source / category | Type | Primary method |
|---|---|---|---|
| 1 | Greenhouse boards | jobs | ATS JSON (`boards-api.greenhouse.io`) |
| 2 | Lever postings | jobs | ATS JSON (`api.lever.co/v0/postings`) |
| 3 | Ashby job board | jobs | ATS JSON (public job board API) |
| 4 | Workable / SmartRecruiters | jobs | public board JSON |
| 5 | GitHub "good first issue" / repos | OSS | GitHub API |
| 6 | GSoC / OSS org pages | gsoc | RSS / sitemap |
| 7 | Kaggle competitions | hackathon | Kaggle API |
| 8 | Devpost hackathons | hackathon | feed |
| 9 | MLH hackathons | hackathon | RSS / sitemap |
| 10 | arXiv | research | API (active labs/authors) |
| 11 | OpenAlex / Crossref | research | API (authors + institutions) |
| 12 | University dept / lab pages | research | RSS / sitemap / scrape |
| 13 | WikiCFP | conference | RSS |
| 14 | grants.gov | grant | API |
| 15 | EU CORDIS / funding portals | grant | API / RSS |
| 16 | NSF / national fellowships | fellowship | RSS / scrape |
| 17 | USAJobs | jobs | API |
| 18 | Adzuna | jobs | API |
| 19 | Remotive | jobs | API |
| 20 | RemoteOK | jobs | API |
| 21 | HN "Who is hiring" | jobs | Algolia API |
| 22 | Wellfound / AngelList | jobs | search API |
| 23 | Company careers pages | jobs | sitemap / scrape |
| 24 | Fellowship aggregators | fellowship | RSS / scrape |
| 25 | Scholarship portals | grant | RSS / scrape |
| 26 | Accelerators / incubators | fellowship | RSS / scrape |
| 27 | Summer schools | research | scrape |
| 28 | Visiting-researcher calls | research | RSS / scrape |
| 29 | Conference travel grants | grant | scrape |
| 30 | Internship aggregators | internship | API where available |
| 31 | General web discovery | any | Tavily / SerpAPI |
| 32 | Generic RSS adapter | any | RSS/Atom |
| 33 | Generic sitemap adapter | any | sitemap.xml |

## Adapter contract

Every source is a thin adapter subclassing
[`ingestion/sources/base.py`](../ingestion/sources/base.py) and implementing:

```python
class SourceAdapter:
    key: str
    access_method: AccessMethod
    async def fetch(self, since: datetime | None) -> list[RawRecord]: ...
    def parse(self, record: RawRecord) -> NormalizedListing | None: ...
```

Adapters must be **schema-tolerant** (never assume a field exists), emit the
canonical `NormalizedListing`, and never raise on a single bad record (skip +
count a parse error instead).

## Anti-brittleness & resilience

- **Content fingerprinting** (`sha256` of normalized payload) → idempotent
  ingestion; re-fetches of unchanged records are no-ops.
- **Source-health monitor** ([`ingestion/health.py`](../ingestion/health.py)):
  tracks `success_rate`, `parse_error_rate`, `freshness_lag`; auto-disables a
  flapping source and raises an admin alert.
- **Rate limiting** ([`ingestion/rate_limit.py`](../ingestion/rate_limit.py)):
  per-host token bucket, exponential backoff + jitter.
- **Conditional GET**: ETag / If-Modified-Since to minimize bandwidth and load.
- **robots.txt** ([`ingestion/robots.py`](../ingestion/robots.py)): checked and
  cached before any non-API fetch.
- **Playwright pool**: reserved for JS-required pages only; bounded concurrency.
- **Identifying user-agent**: the crawler announces itself with a contact URL.

## Normalization

[`ingestion/normalize.py`](../ingestion/normalize.py) maps any adapter output to
the canonical `NormalizedListing` so all downstream stages (dedup, deadline,
ranking) are source-agnostic. Skill extraction and URL canonicalization happen
here.

## Legal / ethical checklist

- [ ] robots.txt honored
- [ ] ToS reviewed; structured endpoint preferred
- [ ] no login-walled / paid data
- [ ] provenance (source + fetched_at) stored
- [ ] PII encrypted at rest; export/delete supported
- [ ] outreach never auto-sent
- [ ] human review for low-confidence deadlines, borderline dedup, all drafts
