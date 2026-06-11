"use client";

import { useEffect, useState } from "react";
import { api, OutreachOut } from "@/lib/api";

const ARTIFACT_LABELS: Record<string, string> = {
  cold_email: "Cold Email (research/lab)",
  cover_letter: "Cover Letter",
  sop: "Statement of Purpose",
  team_pitch: "Team Pitch",
  proposal: "Proposal",
  referral_note: "Referral Note",
};

export function OutreachPanel({ listingId }: { listingId: string }) {
  const [artifact, setArtifact] = useState<OutreachOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editBody, setEditBody] = useState("");
  const [editSubject, setEditSubject] = useState("");
  const [saved, setSaved] = useState(false);

  const userId =
    typeof window !== "undefined" ? localStorage.getItem("userId") ?? undefined : undefined;

  async function generate() {
    if (!userId) return;
    setGenerating(true);
    setError(null);
    try {
      const result = await api.generateOutreach(listingId, userId);
      setArtifact(result);
      setEditBody(result.body);
      setEditSubject(result.subject ?? "");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setGenerating(false);
    }
  }

  async function approve() {
    if (!artifact?.id) return;
    setSaving(true);
    try {
      const updated = await api.updateOutreach(artifact.id, { status: "approved" });
      setArtifact(updated);
      setSaved(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  async function saveEdits() {
    if (!artifact?.id) return;
    setSaving(true);
    try {
      const updated = await api.updateOutreach(artifact.id, { body: editBody, subject: editSubject || undefined });
      setArtifact(updated);
      setEditBody(updated.body);
      setSaved(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  if (!userId) {
    return (
      <div style={{ padding: 16, border: "1px solid #eee", borderRadius: 8, color: "#888" }}>
        <a href="/onboarding" style={{ color: "#0070f3" }}>Set up your profile</a> to generate an outreach draft.
      </div>
    );
  }

  if (!artifact) {
    return (
      <div style={{ padding: 16, border: "1px solid #eee", borderRadius: 8 }}>
        <p style={{ color: "#555", marginTop: 0 }}>
          Generate a draft outreach message. The type (cold email, cover letter, SOP, etc.)
          is determined by the opportunity type — not chosen manually.
        </p>
        <button
          onClick={generate}
          disabled={generating}
          style={{ padding: "10px 20px", borderRadius: 6, border: "none", background: "#0070f3", color: "white", cursor: generating ? "wait" : "pointer" }}
        >
          {generating ? "Generating draft…" : "Generate draft"}
        </button>
        {error && <p style={{ color: "#c00", marginTop: 8 }}>{error}</p>}
      </div>
    );
  }

  const typeLabel = ARTIFACT_LABELS[artifact.artifact_type] ?? artifact.artifact_type;

  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>{typeLabel}</h3>
        <div style={{ display: "flex", gap: 8 }}>
          <span style={{
            fontSize: 12, padding: "3px 10px", borderRadius: 10,
            background: artifact.status === "approved" ? "#e6f4ea" : "#fef7e0",
            color: artifact.status === "approved" ? "#137333" : "#b06000"
          }}>
            {artifact.status}
          </span>
          <span style={{ fontSize: 12, color: "#888" }}>Grounding: {artifact.grounding}</span>
        </div>
      </div>

      {artifact.artifact_type === "cold_email" || artifact.artifact_type === "cover_letter" ? (
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 4, fontSize: 13 }}>Subject</label>
          <input
            type="text"
            value={editSubject}
            onChange={(e) => { setEditSubject(e.target.value); setSaved(false); }}
            style={{ width: "100%", padding: "8px 12px", border: "1px solid #ddd", borderRadius: 6, boxSizing: "border-box" }}
          />
        </div>
      ) : null}

      <label style={{ display: "block", fontWeight: 500, marginBottom: 4, fontSize: 13 }}>Body</label>
      <textarea
        value={editBody}
        onChange={(e) => { setEditBody(e.target.value); setSaved(false); }}
        rows={16}
        style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, fontFamily: "inherit", resize: "vertical", boxSizing: "border-box" }}
      />

      <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button
          onClick={saveEdits}
          disabled={saving}
          style={{ padding: "8px 18px", borderRadius: 6, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          {saving ? "Saving…" : saved ? "✓ Saved" : "Save edits"}
        </button>
        <button
          onClick={approve}
          disabled={saving || artifact.status === "approved"}
          style={{ padding: "8px 18px", borderRadius: 6, border: "none", background: "#137333", color: "white", cursor: artifact.status === "approved" ? "default" : "pointer" }}
        >
          {artifact.status === "approved" ? "✓ Approved" : "Mark as approved"}
        </button>
        <button
          onClick={() => {
            navigator.clipboard.writeText(
              (editSubject ? `Subject: ${editSubject}\n\n` : "") + editBody
            );
          }}
          style={{ padding: "8px 18px", borderRadius: 6, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Copy to clipboard
        </button>
        <button
          onClick={generate}
          style={{ padding: "8px 18px", borderRadius: 6, border: "1px solid #ddd", background: "white", cursor: "pointer", marginLeft: "auto" }}
        >
          Regenerate
        </button>
      </div>

      <p style={{ fontSize: 12, color: "#888", marginTop: 8 }}>
        Drafts are never auto-sent. Review and send manually when ready.
      </p>

      {error && <p style={{ color: "#c00" }}>{error}</p>}
    </div>
  );
}
