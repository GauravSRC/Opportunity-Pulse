"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const SIGNALS: { value: string; label: string; emoji: string }[] = [
  { value: "save", label: "Save", emoji: "🔖" },
  { value: "thumbs_up", label: "Good fit", emoji: "👍" },
  { value: "thumbs_down", label: "Poor fit", emoji: "👎" },
  { value: "dismiss", label: "Dismiss", emoji: "✕" },
  { value: "applied", label: "Applied", emoji: "✅" },
];

export function FeedbackButtons({
  listingId,
  userId,
  onFeedback,
}: {
  listingId: string;
  userId: string;
  onFeedback?: (signal: string) => void;
}) {
  const [sent, setSent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick(signal: string) {
    setLoading(true);
    try {
      await api.submitFeedback(userId, listingId, signal);
      setSent(signal);
      onFeedback?.(signal);
    } catch {
      // best-effort; don't disrupt UX
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", gap: 6 }}>
      {SIGNALS.map(({ value, label, emoji }) => (
        <button
          key={value}
          title={label}
          disabled={loading || sent !== null}
          onClick={() => handleClick(value)}
          style={{
            background: sent === value ? "#e8f0fe" : "#f5f5f5",
            border: "none",
            borderRadius: 6,
            padding: "4px 8px",
            cursor: sent ? "default" : "pointer",
            fontSize: 14,
            opacity: sent && sent !== value ? 0.4 : 1,
          }}
        >
          {emoji}
        </button>
      ))}
    </div>
  );
}
