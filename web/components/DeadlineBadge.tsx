export function DeadlineBadge({
  kind,
  resolvedDate,
}: {
  kind: "fixed" | "rolling" | "relative" | "unknown";
  resolvedDate?: string | null;
}) {
  const label =
    kind === "rolling"
      ? "Rolling"
      : kind === "unknown"
        ? "No deadline found"
        : resolvedDate ?? "Relative";
  return (
    <span
      style={{
        background: kind === "rolling" ? "#fef7e0" : "#e8f0fe",
        borderRadius: 12,
        padding: "2px 10px",
        fontSize: 12,
      }}
    >
      {label}
    </span>
  );
}
