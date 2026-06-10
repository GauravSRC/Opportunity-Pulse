import Link from "next/link";

const links = [
  ["/onboarding", "Onboarding — build your profile"],
  ["/feed", "Feed — ranked opportunities"],
  ["/deadlines", "Deadline tracker"],
  ["/settings", "Settings & alerts"],
];

export default function Home() {
  return (
    <div>
      <h1>OpportunityPulse</h1>
      <p>
        Find, dedup, rank, and reach out to opportunities across 30+ sources —
        with the right outreach artifact for each.
      </p>
      <ul>
        {links.map(([href, label]) => (
          <li key={href}>
            <Link href={href}>{label}</Link>
          </li>
        ))}
      </ul>
      <p style={{ color: "#888" }}>
        Phase-0 scaffold — screens are stubs until the API is wired in Phase 1.
      </p>
    </div>
  );
}
