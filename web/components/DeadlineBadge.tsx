import { DeadlineOut } from "@/lib/api";

export function DeadlineBadge({ deadline }: { deadline: DeadlineOut }) {
  const { kind, resolved_date, confidence, needs_review } = deadline;

  let label: string;
  let bg: string;
  let color = "#333";

  if (kind === "rolling") {
    label = "Rolling";
    bg = "#fef7e0";
  } else if (kind === "fixed" && resolved_date) {
    const d = new Date(resolved_date);
    const now = new Date();
    const daysLeft = Math.ceil((d.getTime() - now.getTime()) / 86400000);
    label = daysLeft <= 0 ? "Closed" : daysLeft <= 7 ? `${daysLeft}d left` : d.toLocaleDateString();
    bg = daysLeft <= 7 ? "#fce8e6" : "#e8f0fe";
    color = daysLeft <= 7 ? "#c5221f" : "#1a73e8";
  } else if (kind === "relative") {
    label = deadline.raw_phrase ?? "Relative deadline";
    bg = "#fef7e0";
  } else {
    label = "No deadline";
    bg = "#f5f5f5";
    color = "#888";
  }

  return (
    <span
      title={needs_review ? "Low confidence — may need review" : `Confidence: ${Math.round(confidence * 100)}%`}
      style={{ background: bg, color, borderRadius: 12, padding: "2px 10px", fontSize: 12, cursor: "default" }}
    >
      {needs_review ? "⚠ " : ""}{label}
    </span>
  );
}
