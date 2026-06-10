import Link from "next/link";
import { MatchScoreBadge } from "./MatchScoreBadge";

export interface OpportunityCardProps {
  id?: string;
  title: string;
  org?: string;
  type: string;
  score?: number;
  deadline?: string;
}

export function OpportunityCard({
  id = "example",
  title,
  org,
  type,
  score = 0,
  deadline,
}: OpportunityCardProps) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16, margin: "12px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>{title}</strong>
        <MatchScoreBadge score={score} />
      </div>
      <div style={{ color: "#666" }}>
        {org} · {type}
        {deadline ? ` · due ${deadline}` : ""}
      </div>
      <Link href={`/opportunity/${id}`}>View details</Link>
    </div>
  );
}
