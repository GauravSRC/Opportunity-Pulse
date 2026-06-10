# OpportunityPulse Web (Next.js)

The user-facing app. Phase-0 scaffold: stub pages/components that establish the
information architecture. Wire to the API in Phase 1+.

## Run

```bash
npm install
npm run dev   # http://localhost:3000  (API base from NEXT_PUBLIC_API_BASE_URL)
```

## Screens (App Router)

| Route | Purpose |
|---|---|
| `/onboarding` | résumé drop + skill/intent/location setup -> first feed |
| `/feed` | ranked opportunity cards with filter/sort |
| `/opportunity/[id]` | detail + "Why it matched" panel + "also seen on" |
| `/deadlines` | urgency-sorted tracker, add-to-calendar |
| `/outreach/[id]` | type-routed draft (cold email ONLY for research/lab) |
| `/settings` | profile editor + alert settings |

## Components

- `OpportunityCard`, `MatchScoreBadge`, `WhyMatchedPanel`, `DeadlineBadge`,
  `OutreachPanel`, `FeedbackButtons` (see `components/`).

## API client

`lib/api.ts` centralizes calls to the FastAPI backend. The outreach UI renders
whatever `artifact_type` the server returns — it must not assume "cold email".
