// Centralized API client for the FastAPI backend.
// The outreach endpoint returns an artifact_type decided server-side —
// the UI renders whatever comes back and must not assume "cold email".

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ────────────────────────────────────────────────────────────────────

export interface DeadlineOut {
  kind: "fixed" | "rolling" | "relative" | "unknown";
  resolved_date?: string;
  raw_phrase?: string;
  confidence: number;
  needs_review: boolean;
  extractor?: string;
}

export interface OpportunityOut {
  id: string;
  title: string;
  org?: string;
  type: string;
  location?: string;
  is_remote: boolean;
  url: string;
  posted_at?: string;
  skills: string[];
  score?: number;
  deadline?: DeadlineOut;
  also_seen_on: string[];
}

export interface FeedPage {
  items: OpportunityOut[];
  page: number;
  limit: number;
  total: number;
}

export interface ScoreComponents {
  semantic: number;
  skill_overlap: number;
  recency: number;
  urgency: number;
  feedback: number;
}

export interface ExplanationOut {
  listing_id: string;
  score: number;
  components: ScoreComponents;
  matched_skills: string[];
  model_version: string;
}

export interface ProfileOut {
  id: string;
  user_id: string;
  headline?: string;
  skills: string[];
  intents: string[];
  locations: string[];
  is_remote_ok: boolean;
}

export interface OutreachOut {
  id?: string;
  artifact_type: string;
  subject?: string;
  body: string;
  rag_sources: { kind: string; url: string }[];
  status: "draft" | "approved" | "discarded";
  grounding: string;
}

// ── API client ───────────────────────────────────────────────────────────────

export const api = {
  // Feed / search
  searchOpportunities: (params: URLSearchParams) =>
    http<FeedPage>(`/opportunities?${params}`),

  getOpportunity: (id: string, userId?: string) =>
    http<OpportunityOut>(`/opportunities/${id}${userId ? `?user_id=${userId}` : ""}`),

  getExplanation: (id: string, userId: string) =>
    http<ExplanationOut>(`/opportunities/${id}/explanation?user_id=${userId}`),

  // Profile
  createProfile: (body: {
    email: string;
    headline?: string;
    skills: string[];
    intents: string[];
    locations: string[];
    is_remote_ok: boolean;
  }) => http<ProfileOut>("/profiles", { method: "POST", body: JSON.stringify(body) }),

  getProfile: (id: string) => http<ProfileOut>(`/profiles/${id}`),

  updateProfile: (id: string, body: Partial<ProfileOut>) =>
    http<ProfileOut>(`/profiles/${id}`, { method: "PATCH", body: JSON.stringify(body) }),

  // Outreach
  generateOutreach: (listingId: string, userId: string) =>
    http<OutreachOut>(`/opportunities/${listingId}/outreach`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    }),

  updateOutreach: (artifactId: string, body: { body?: string; subject?: string; status?: string }) =>
    http<OutreachOut>(`/outreach/${artifactId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  // Deadline extract (ad hoc)
  extractDeadline: (text: string) =>
    http<DeadlineOut>("/deadlines/extract", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  // Feedback
  submitFeedback: (userId: string, listingId: string, signal: string) =>
    http<{ ok: boolean }>("/feedback", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, listing_id: listingId, signal }),
    }),

  // Admin
  adminHealth: () => http<Record<string, unknown>>("/admin/health"),

  // Sources
  syncSources: () => http<{ synced: number }>("/sources/sync", { method: "POST" }),
};
