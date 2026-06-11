import type { ReactNode } from "react";
import Link from "next/link";

export const metadata = {
  title: "OpportunityPulse",
  description:
    "Semantic discovery, ranking, and outreach for jobs, research, fellowships, hackathons, and grants.",
};

const NAV = [
  { href: "/feed", label: "Feed" },
  { href: "/deadlines", label: "Deadlines" },
  { href: "/settings", label: "Settings" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
          background: "#fafafa",
        }}
      >
        <header
          style={{
            padding: "0 24px",
            borderBottom: "1px solid #eee",
            background: "white",
            display: "flex",
            alignItems: "center",
            height: 52,
            gap: 32,
          }}
        >
          <Link href="/" style={{ fontWeight: 700, fontSize: 17, color: "#0070f3", textDecoration: "none" }}>
            OpportunityPulse
          </Link>
          <nav style={{ display: "flex", gap: 24 }}>
            {NAV.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                style={{ color: "#444", textDecoration: "none", fontSize: 14, fontWeight: 500 }}
              >
                {label}
              </Link>
            ))}
          </nav>
          <div style={{ marginLeft: "auto" }}>
            <Link
              href="/onboarding"
              style={{
                fontSize: 13,
                padding: "6px 14px",
                borderRadius: 6,
                background: "#0070f3",
                color: "white",
                textDecoration: "none",
                fontWeight: 500,
              }}
            >
              + Profile
            </Link>
          </div>
        </header>
        <main style={{ padding: "24px 24px", maxWidth: 1000, margin: "0 auto" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
