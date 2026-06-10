import type { ReactNode } from "react";

export const metadata = {
  title: "OpportunityPulse",
  description:
    "Semantic discovery, ranking, and outreach for jobs, research, fellowships, hackathons, and grants.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        }}
      >
        <header
          style={{
            padding: "12px 24px",
            borderBottom: "1px solid #eee",
            fontWeight: 600,
          }}
        >
          OpportunityPulse
        </header>
        <main style={{ padding: 24, maxWidth: 960, margin: "0 auto" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
