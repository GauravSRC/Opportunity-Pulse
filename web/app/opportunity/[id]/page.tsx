"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, OpportunityOut, ExplanationOut } from "@/lib/api";
import { DeadlineBadge } from "@/components/DeadlineBadge";
import { FeedbackButtons } from "@/components/FeedbackButtons";
import { WhyMatchedPanel } from "@/components/WhyMatchedPanel";
import { MatchScoreBadge } from "@/components/MatchScoreBadge";

export default function OpportunityDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const [opp, setOpp] = useState<OpportunityOut | null>(null);
  const [explanation, setExplanation] = useState<ExplanationOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [outreachLoading, setOutreachLoading] = useState(false);
  const [outreachError, setOutreachError] = useState<string | null>(null);

  const userId =
    typeof window !== "undefined" ? localStorage.getItem("userId") ?? undefined : undefined;

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getOpportunity(id, userId ?? undefined);
        setOpp(data);
        if (userId) {
          try {
            const expl = await api.getExplanation(id, userId);
            setExplanation(expl);
          } catch {
            // no explanation yet — skip
          }
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, userId]);

  async function generateOutreach() {
    if (!userId) return;
    setOutreachLoading(true);
    setOutreachError(null);
    try {
      await api.generateOutreach(id, userId);
      window.location.href = `/outreach/${id}`;
    } catch (e: unknown) {
      setOutreachError(e instanceof Error ? e.message : String(e));
    } finally {
      setOutreachLoading(false);
    }
  }

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{ color: "#c00" }}>Error: {error}</p>;
  if (!opp) return <p>Opportunity not found.</p>;

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Link href="/feed" style={{ color: "#0070f3", textDecoration: "none" }}>← Back to feed</Link>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <h2 style={{ marginTop: 0, marginBottom: 8 }}>{opp.title}</h2>
        {opp.score !== undefined && opp.score !== null && (
          <MatchScoreBadge score={opp.score} />
        )}
      </div>

      <div style={{ color: "#555", marginBottom: 12 }}>
        {opp.org && <span style={{ fontWeight: 500 }}>{opp.org}</span>}
        {opp.org && <span> · </span>}
        <span style={{ textTransform: "capitalize" }}>{opp.type}</span>
        {opp.location && <span> · {opp.location}</span>}
        {opp.is_remote && (
          <span style={{ marginLeft: 8, fontSize: 12, background: "#e6f4ea", color: "#137333", padding: "2px 8px", borderRadius: 10 }}>
            Remote
          </span>
        )}
      </div>

      {opp.deadline && (
        <div style={{ marginBottom: 12 }}>
          <DeadlineBadge deadline={opp.deadline} />
        </div>
      )}

      {opp.skills.length > 0 && (
        <div style={{ marginBottom: 16, display: "flex", flexWrap: "wrap", gap: 6 }}>
          {opp.skills.map((s) => (
            <span key={s} style={{ fontSize: 12, background: "#f0f0f0", padding: "3px 10px", borderRadius: 12 }}>{s}</span>
          ))}
        </div>
      )}

      {opp.also_seen_on.length > 0 && (
        <div style={{ marginBottom: 16, padding: 12, background: "#f8f9fa", borderRadius: 6, fontSize: 13 }}>
          Also seen on:{" "}
          {opp.also_seen_on.map((url) => (
            <a key={url} href={url} target="_blank" rel="noopener noreferrer" style={{ color: "#0070f3", marginRight: 8 }}>
              {new URL(url).hostname}
            </a>
          ))}
        </div>
      )}

      <div style={{ marginBottom: 20 }}>
        <a
          href={opp.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: "inline-block", padding: "10px 20px", background: "#0070f3", color: "white", borderRadius: 6, textDecoration: "none", marginRight: 12 }}
        >
          View original →
        </a>
        {userId && (
          <button
            onClick={generateOutreach}
            disabled={outreachLoading}
            style={{ padding: "10px 20px", borderRadius: 6, border: "1.5px solid #0070f3", color: "#0070f3", background: "white", cursor: outreachLoading ? "wait" : "pointer" }}
          >
            {outreachLoading ? "Generating…" : "Generate outreach draft"}
          </button>
        )}
        {!userId && (
          <Link href="/onboarding" style={{ color: "#0070f3", marginLeft: 12 }}>
            Set up profile to generate outreach →
          </Link>
        )}
      </div>

      {outreachError && (
        <div style={{ marginBottom: 16, padding: 12, background: "#fff0f0", color: "#c00", borderRadius: 6 }}>
          {outreachError}
        </div>
      )}

      {userId && (
        <div style={{ marginBottom: 20 }}>
          <FeedbackButtons listingId={id} userId={userId} onFeedback={() => {}} />
        </div>
      )}

      {/* Why it matched */}
      {explanation ? (
        <WhyMatchedPanel
          components={explanation.components}
          matchedSkills={explanation.matched_skills}
        />
      ) : userId ? (
        <div style={{ padding: 16, border: "1px solid #eee", borderRadius: 8, color: "#888" }}>
          No ranking data yet for this opportunity. Go back to feed and let ranking run.
        </div>
      ) : null}
    </div>
  );
}
