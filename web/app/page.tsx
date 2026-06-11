import Link from "next/link";

export default function Home() {
  return (
    <div style={{ maxWidth: 640 }}>
      <h1 style={{ marginTop: 0 }}>OpportunityPulse</h1>
      <p style={{ fontSize: 17, color: "#444", lineHeight: 1.6 }}>
        Semantic discovery, ranking, and outreach for jobs, internships, research,
        fellowships, hackathons, and grants — across 30+ sources.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 28 }}>
        {[
          {
            href: "/onboarding",
            title: "Set up profile",
            desc: "Tell us your skills, interests, and locations to get a personalized ranked feed.",
            cta: "Get started →",
            bg: "#0070f3",
          },
          {
            href: "/feed",
            title: "Browse feed",
            desc: "Ranked opportunities from all sources. Filter by type, remote, deadline.",
            cta: "Go to feed →",
            bg: "#1a73e8",
          },
          {
            href: "/deadlines",
            title: "Deadline tracker",
            desc: "Urgency-sorted deadline view with .ics calendar export.",
            cta: "View deadlines →",
            bg: "#137333",
          },
          {
            href: "/settings",
            title: "Settings",
            desc: "Edit your profile, skills, and alert preferences.",
            cta: "Edit settings →",
            bg: "#b06000",
          },
        ].map(({ href, title, desc, cta, bg }) => (
          <Link
            key={href}
            href={href}
            style={{
              display: "block",
              padding: 20,
              borderRadius: 10,
              border: "1px solid #eee",
              textDecoration: "none",
              color: "inherit",
              transition: "box-shadow 0.15s",
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: 8, color: bg }}>{title}</h3>
            <p style={{ fontSize: 14, color: "#555", marginBottom: 12 }}>{desc}</p>
            <span style={{ fontSize: 14, color: bg, fontWeight: 500 }}>{cta}</span>
          </Link>
        ))}
      </div>

      <div style={{ marginTop: 32, padding: 16, background: "#f8f9fa", borderRadius: 8, fontSize: 13, color: "#666" }}>
        <strong>Quick start:</strong> Run{" "}
        <code style={{ background: "#e8e8e8", padding: "2px 6px", borderRadius: 4 }}>
          python scripts/demo_seed.py
        </code>{" "}
        to load demo data, then{" "}
        <code style={{ background: "#e8e8e8", padding: "2px 6px", borderRadius: 4 }}>
          uvicorn app.main:app --reload
        </code>{" "}
        (from <code style={{ background: "#e8e8e8", padding: "2px 6px", borderRadius: 4 }}>backend/</code>).
      </div>
    </div>
  );
}
