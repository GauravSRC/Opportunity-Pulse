"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { OpportunityOut, FeedPage } from "@/lib/api";
import { MatchScoreBadge } from "@/components/MatchScoreBadge";
import { DeadlineBadge } from "@/components/DeadlineBadge";
import { FeedbackButtons } from "@/components/FeedbackButtons";

const OPPORTUNITY_TYPES = [
  "all", "job", "internship", "research", "fellowship",
  "hackathon", "grant", "gsoc", "conference",
];

export default function FeedPage() {
  const [items, setItems] = useState<OpportunityOut[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // filters
  const [q, setQ] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [remoteOnly, setRemoteOnly] = useState(false);

  const userId =
    typeof window !== "undefined" ? localStorage.getItem("userId") ?? undefined : undefined;

  const fetchFeed = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(page), limit: "20" });
      if (q) params.set("q", q);
      if (typeFilter !== "all") params.set("type", typeFilter);
      if (remoteOnly) params.set("remote", "true");
      if (userId) params.set("user_id", userId);
      const data: FeedPage = await api.searchOpportunities(params);
      setItems(data.items);
      setTotal(data.total);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [q, typeFilter, remoteOnly, page, userId]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  const limit = 20;
  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Opportunity Feed</h2>

      {/* Search + filters */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
        <input
          type="text"
          placeholder="Search title, description…"
          value={q}
          onChange={(e) => { setQ(e.target.value); setPage(1); }}
          style={{ flex: 1, minWidth: 200, padding: "8px 12px", border: "1px solid #ddd", borderRadius: 6 }}
        />
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          style={{ padding: "8px 12px", border: "1px solid #ddd", borderRadius: 6 }}
        >
          {OPPORTUNITY_TYPES.map((t) => (
            <option key={t} value={t}>{t === "all" ? "All types" : t}</option>
          ))}
        </select>
        <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <input
            type="checkbox"
            checked={remoteOnly}
            onChange={(e) => { setRemoteOnly(e.target.checked); setPage(1); }}
          />
          Remote only
        </label>
        {!userId && (
          <Link
            href="/onboarding"
            style={{ padding: "8px 16px", background: "#0070f3", color: "white", borderRadius: 6, textDecoration: "none" }}
          >
            Set up profile for personalized ranking →
          </Link>
        )}
      </div>

      {/* Status */}
      {error && (
        <div style={{ color: "#c00", padding: 12, background: "#fff0f0", borderRadius: 6, marginBottom: 16 }}>
          Error: {error}. Make sure the backend is running at localhost:8000.
        </div>
      )}
      {loading && <p style={{ color: "#888" }}>Loading…</p>}
      {!loading && !error && (
        <p style={{ color: "#888", marginBottom: 12 }}>
          {total} opportunities{userId ? " (personalized)" : ""}
        </p>
      )}

      {/* Cards */}
      {items.map((opp) => (
        <div
          key={opp.id}
          style={{ border: "1px solid #eee", borderRadius: 8, padding: 16, marginBottom: 12 }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ flex: 1 }}>
              <Link
                href={`/opportunity/${opp.id}`}
                style={{ fontWeight: 600, fontSize: 16, color: "#111", textDecoration: "none" }}
              >
                {opp.title}
              </Link>
              <div style={{ color: "#555", marginTop: 4 }}>
                {opp.org && <span>{opp.org} · </span>}
                <span style={{ textTransform: "capitalize" }}>{opp.type}</span>
                {opp.location && <span> · {opp.location}</span>}
                {opp.is_remote && <span style={{ marginLeft: 6, fontSize: 12, background: "#e6f4ea", color: "#137333", padding: "2px 6px", borderRadius: 10 }}>Remote</span>}
              </div>
              {opp.skills.length > 0 && (
                <div style={{ marginTop: 6, display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {opp.skills.slice(0, 5).map((s) => (
                    <span key={s} style={{ fontSize: 11, background: "#f0f0f0", padding: "2px 8px", borderRadius: 10 }}>{s}</span>
                  ))}
                  {opp.skills.length > 5 && <span style={{ fontSize: 11, color: "#888" }}>+{opp.skills.length - 5}</span>}
                </div>
              )}
            </div>
            <div style={{ textAlign: "right", marginLeft: 12 }}>
              <MatchScoreBadge score={opp.score ?? 0} />
              {opp.deadline && <div style={{ marginTop: 4 }}><DeadlineBadge deadline={opp.deadline} /></div>}
            </div>
          </div>
          <div style={{ marginTop: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            {userId && (
              <FeedbackButtons
                listingId={opp.id}
                userId={userId}
                onFeedback={() => {}}
              />
            )}
            <a href={opp.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 13, color: "#0070f3" }}>
              View original →
            </a>
          </div>
        </div>
      ))}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
            style={{ padding: "6px 14px", borderRadius: 6, border: "1px solid #ddd", cursor: "pointer" }}>
            ← Prev
          </button>
          <span style={{ padding: "6px 12px" }}>Page {page} / {totalPages}</span>
          <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
            style={{ padding: "6px 14px", borderRadius: 6, border: "1px solid #ddd", cursor: "pointer" }}>
            Next →
          </button>
        </div>
      )}

      {!loading && items.length === 0 && !error && (
        <div style={{ padding: 24, textAlign: "center", color: "#888" }}>
          <p>No opportunities found.</p>
          <p>Run <code>POST /sources/sync</code> then <code>POST /sources/demo_fixture/ingest</code> to load demo data.</p>
        </div>
      )}
    </div>
  );
}
