// Centralized API client for the FastAPI backend.
// The outreach endpoint returns an `artifact_type` decided server-side — the UI
// renders whatever comes back and must not assume "cold email".

const BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  // TODO(phase-1+): type these responses against the backend schemas.
  searchOpportunities: (query: string) =>
    http<unknown>(`/opportunities?${query}`),
  getOpportunity: (id: string) => http<unknown>(`/opportunities/${id}`),
  getExplanation: (id: string, userId: string) =>
    http<unknown>(`/opportunities/${id}/explanation?user_id=${userId}`),
  generateOutreach: (id: string, body: unknown) =>
    http<unknown>(`/opportunities/${id}/outreach`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  submitFeedback: (body: unknown) =>
    http<unknown>(`/feedback`, { method: "POST", body: JSON.stringify(body) }),
};
