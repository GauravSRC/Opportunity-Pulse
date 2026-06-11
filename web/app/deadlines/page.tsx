"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, OpportunityOut } from "@/lib/api";
import { DeadlineBadge } from "@/components/DeadlineBadge";

type DeadlineItem = {
  opp: OpportunityOut;
  daysLeft: number | null;
};

function daysUntil(dateStr: string): number {
  return Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000);
}

function urgencyColor(days: number | null): string {
  if (days === null) return "#888";
  if (days <= 0) return "#c5221f";
  if (days <= 7) return "#b06000";
  if (days <= 21) return "#0070f3";
  return "#137333";
}

function generateICS(items: DeadlineItem[]): string {
  const ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//OpportunityPulse//EN",
    ...items
      .filter((i) => i.opp.deadline?.resolved_date)
      .map((i) => {
        const d = new Date(i.opp.deadline!.resolved_date!);
        const dtStr = d.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
        return [
          "BEGIN:VEVENT",
          `SUMMARY:Deadline: ${i.opp.title} @ ${i.opp.org ?? "unknown"}`,
          `DTSTART:${dtStr}`,
          `DTEND:${dtStr}`,
          `URL:${i.opp.url}`,
          "END:VEVENT",
        ].join("\n");
      }),
    "END:VCALENDAR",
  ].join("\n");
  return ics;
}

export default function DeadlinesPage() {
  const [items, setItems] = useState<DeadlineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterActive, setFilterActive] = useState(false);

  const userId =
    typeof window !== "undefined" ? localStorage.getItem("userId") ?? undefined : undefined;

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams({ limit: "100" });
        if (userId) params.set("user_id", userId);
        const data = await api.searchOpportunities(params);
        const withDeadlines: DeadlineItem[] = data.items
          .filter((opp) => opp.deadline && opp.deadline.kind !== "unknown")
          .map((opp) => ({
            opp,
            daysLeft: opp.deadline?.resolved_date ? daysUntil(opp.deadline.resolved_date) : null,
          }));
        // Sort: fixed deadlines soonest first, then rolling
        withDeadlines.sort((a, b) => {
          if (a.daysLeft === null && b.daysLeft === null) return 0;
          if (a.daysLeft === null) return 1;
          if (b.daysLeft === null) return -1;
          return a.daysLeft - b.daysLeft;
        });
        setItems(withDeadlines);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  function downloadICS() {
    const content = generateICS(items);
    const blob = new Blob([content], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "opportunitypulse_deadlines.ics";
    a.click();
    URL.revokeObjectURL(url);
  }

  const displayed = filterActive
    ? items.filter((i) => i.daysLeft !== null && i.daysLeft >= 0 && i.daysLeft <= 30)
    : items;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ marginTop: 0 }}>Deadline Tracker</h2>
        <div style={{ display: "flex", gap: 10 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14 }}>
            <input
              type="checkbox"
              checked={filterActive}
              onChange={(e) => setFilterActive(e.target.checked)}
            />
            Closing within 30 days
          </label>
          <button
            onClick={downloadICS}
            disabled={items.length === 0}
            style={{ padding: "6px 14px", borderRadius: 6, border: "1px solid #ddd", cursor: "pointer", fontSize: 13 }}
          >
            Export .ics
          </button>
        </div>
      </div>

      {loading && <p style={{ color: "#888" }}>Loading…</p>}
      {error && <p style={{ color: "#c00" }}>Error: {error}</p>}

      {!loading && displayed.length === 0 && (
        <div style={{ padding: 24, textAlign: "center", color: "#888" }}>
          No deadlines found. Make sure the backend is running and data is ingested.
        </div>
      )}

      {displayed.map(({ opp, daysLeft }) => (
        <div
          key={opp.id}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 16px",
            borderBottom: "1px solid #f0f0f0",
            borderLeft: `4px solid ${urgencyColor(daysLeft)}`,
            marginBottom: 2,
          }}
        >
          <div>
            <Link
              href={`/opportunity/${opp.id}`}
              style={{ fontWeight: 500, color: "#111", textDecoration: "none" }}
            >
              {opp.title}
            </Link>
            <div style={{ fontSize: 13, color: "#666", marginTop: 2 }}>
              {opp.org && <span>{opp.org} · </span>}
              <span style={{ textTransform: "capitalize" }}>{opp.type}</span>
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            {opp.deadline && <DeadlineBadge deadline={opp.deadline} />}
            {daysLeft !== null && daysLeft > 0 && (
              <div style={{ fontSize: 12, color: urgencyColor(daysLeft), marginTop: 4 }}>
                {daysLeft}d remaining
              </div>
            )}
            {daysLeft !== null && daysLeft <= 0 && (
              <div style={{ fontSize: 12, color: "#c5221f", marginTop: 4 }}>Closed</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
