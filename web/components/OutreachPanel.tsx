"use client";

import { useState } from "react";

// Human-readable labels for each artifact type the server may return.
const ARTIFACT_LABELS: Record<string, string> = {
  cold_email: "Cold email (research/lab)",
  cover_letter: "Cover letter",
  sop: "Statement of purpose",
  team_pitch: "Team-up pitch",
  proposal: "Proposal",
  referral_note: "Referral note",
};

export function OutreachPanel({ listingId }: { listingId: string }) {
  const [artifactType] = useState<string | null>(null);
  // TODO(phase-4): POST /opportunities/{listingId}/outreach -> {artifact_type, body}.
  // Render whatever artifact_type comes back; never hardcode "cold email".
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
      <p>
        Draft type:{" "}
        <strong>
          {artifactType ? ARTIFACT_LABELS[artifactType] ?? artifactType : "decided by opportunity type"}
        </strong>
      </p>
      <p style={{ color: "#888" }}>
        TODO(phase-4): generate, edit, and approve the draft (never auto-sent).
        Listing: {listingId}
      </p>
    </div>
  );
}
