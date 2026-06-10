import { OutreachPanel } from "@/components/OutreachPanel";

export default function OutreachPage({ params }: { params: { id: string } }) {
  // TODO(phase-4): POST /opportunities/{id}/outreach.
  // The artifact_type is decided server-side (cold email ONLY for research/lab);
  // render whatever comes back — never assume "cold email".
  return (
    <div>
      <h2>Outreach for {params.id}</h2>
      <OutreachPanel listingId={params.id} />
    </div>
  );
}
