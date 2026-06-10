import { WhyMatchedPanel } from "@/components/WhyMatchedPanel";

export default function OpportunityDetail({
  params,
}: {
  params: { id: string };
}) {
  // TODO(phase-1/2): fetch GET /opportunities/{id} and /explanation.
  return (
    <div>
      <h2>Opportunity {params.id}</h2>
      <p style={{ color: "#888" }}>
        TODO(phase-1): detail from GET /opportunities/{params.id}.
      </p>
      <WhyMatchedPanel
        components={{
          semantic: 0,
          skill_overlap: 0,
          recency: 0,
          urgency: 0,
        }}
        matchedSkills={[]}
      />
    </div>
  );
}
