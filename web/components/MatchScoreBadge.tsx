export function MatchScoreBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct >= 70 ? "#137333" : pct >= 40 ? "#b06000" : "#888";
  return (
    <span
      style={{
        background: "#f1f3f4",
        color,
        borderRadius: 12,
        padding: "2px 10px",
        fontSize: 12,
        fontWeight: 600,
      }}
      title="Semantic + skill + recency + urgency match"
    >
      {pct}% match
    </span>
  );
}
