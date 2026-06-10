export interface ScoreComponents {
  semantic: number;
  skill_overlap: number;
  recency: number;
  urgency: number;
  feedback?: number;
}

export function WhyMatchedPanel({
  components,
  matchedSkills,
}: {
  components: ScoreComponents;
  matchedSkills: string[];
}) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Why it matched</h3>
      {Object.entries(components).map(([k, v]) => (
        <div key={k} style={{ margin: "6px 0" }}>
          <span style={{ display: "inline-block", width: 120 }}>{k}</span>
          <span
            style={{
              display: "inline-block",
              height: 8,
              width: Math.max(2, (v ?? 0) * 200),
              background: "#1a73e8",
              borderRadius: 4,
              verticalAlign: "middle",
            }}
          />
        </div>
      ))}
      <div style={{ marginTop: 8, color: "#666" }}>
        Matched skills: {matchedSkills.length ? matchedSkills.join(", ") : "—"}
      </div>
    </div>
  );
}
