import { OpportunityCard } from "@/components/OpportunityCard";

export default function FeedPage() {
  // TODO(phase-1): fetch GET /opportunities and render ranked cards + filters.
  return (
    <div>
      <h2>Feed</h2>
      <p style={{ color: "#888" }}>
        TODO(phase-1): ranked results from GET /opportunities.
      </p>
      <OpportunityCard
        title="Example: Summer Research Intern"
        org="Vision Lab"
        type="research"
        score={0.0}
      />
    </div>
  );
}
