"use client";

// TODO(phase-6): POST /feedback with the chosen signal.
const SIGNALS = ["save", "dismiss", "thumbs_up", "thumbs_down", "applied"] as const;

export function FeedbackButtons({ listingId }: { listingId: string }) {
  return (
    <div style={{ display: "flex", gap: 8 }}>
      {SIGNALS.map((s) => (
        <button key={s} title={`Send "${s}" for ${listingId}`}>
          {s}
        </button>
      ))}
    </div>
  );
}
