"use client";

import Link from "next/link";
import { OutreachPanel } from "@/components/OutreachPanel";

export default function OutreachPage({ params }: { params: { id: string } }) {
  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Link href={`/opportunity/${params.id}`} style={{ color: "#0070f3", textDecoration: "none" }}>
          ← Back to opportunity
        </Link>
      </div>
      <h2 style={{ marginTop: 0 }}>Outreach Draft</h2>
      <p style={{ color: "#666", marginBottom: 20 }}>
        The draft type (cold email, cover letter, SOP, team pitch, etc.) is determined
        server-side by the opportunity type.
      </p>
      <OutreachPanel listingId={params.id} />
    </div>
  );
}
