"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const INTENTS = ["job", "internship", "research", "fellowship", "hackathon", "grant"];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [headline, setHeadline] = useState("");
  const [skillsRaw, setSkillsRaw] = useState("");
  const [selectedIntents, setSelectedIntents] = useState<string[]>([]);
  const [locationsRaw, setLocationsRaw] = useState("");
  const [isRemoteOk, setIsRemoteOk] = useState(true);

  function toggleIntent(intent: string) {
    setSelectedIntents((prev) =>
      prev.includes(intent) ? prev.filter((i) => i !== intent) : [...prev, intent]
    );
  }

  async function handleSubmit() {
    setError(null);
    if (!email.trim()) { setError("Email is required."); return; }
    const skills = skillsRaw.split(",").map((s) => s.trim()).filter(Boolean);
    const locations = locationsRaw.split(",").map((s) => s.trim()).filter(Boolean);

    setLoading(true);
    try {
      const profile = await api.createProfile({
        email: email.trim(),
        headline: headline.trim() || undefined,
        skills,
        intents: selectedIntents,
        locations,
        is_remote_ok: isRemoteOk,
      });
      localStorage.setItem("userId", profile.user_id);
      localStorage.setItem("profileId", profile.id);
      router.push("/feed");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const stepLabel = ["Your background", "What you want", "Preferences"];

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      <h2 style={{ marginTop: 0 }}>Set Up Your Profile</h2>

      {/* Progress */}
      <div style={{ display: "flex", gap: 8, marginBottom: 28 }}>
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            style={{
              flex: 1,
              height: 4,
              borderRadius: 2,
              background: s <= step ? "#0070f3" : "#eee",
              transition: "background 0.2s",
            }}
          />
        ))}
      </div>
      <p style={{ color: "#888", marginBottom: 24 }}>Step {step} of 3: {stepLabel[step - 1]}</p>

      {step === 1 && (
        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Email *</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
          />
          <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Headline (optional)</label>
          <input
            type="text"
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            placeholder="e.g. CS Student | ML & Backend"
            style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
          />
          <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Skills (comma-separated)</label>
          <input
            type="text"
            value={skillsRaw}
            onChange={(e) => setSkillsRaw(e.target.value)}
            placeholder="Python, Machine Learning, React, SQL"
            style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, boxSizing: "border-box" }}
          />
        </div>
      )}

      {step === 2 && (
        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 12 }}>
            What types of opportunities interest you? (pick all that apply)
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {INTENTS.map((intent) => (
              <button
                key={intent}
                onClick={() => toggleIntent(intent)}
                style={{
                  padding: "8px 18px",
                  borderRadius: 20,
                  border: "1.5px solid",
                  borderColor: selectedIntents.includes(intent) ? "#0070f3" : "#ddd",
                  background: selectedIntents.includes(intent) ? "#e8f0fe" : "white",
                  color: selectedIntents.includes(intent) ? "#0070f3" : "#333",
                  cursor: "pointer",
                  fontWeight: selectedIntents.includes(intent) ? 600 : 400,
                  textTransform: "capitalize",
                }}
              >
                {intent}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>
            Preferred locations (comma-separated)
          </label>
          <input
            type="text"
            value={locationsRaw}
            onChange={(e) => setLocationsRaw(e.target.value)}
            placeholder="Remote, San Francisco, New York"
            style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
          />
          <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={isRemoteOk}
              onChange={(e) => setIsRemoteOk(e.target.checked)}
              style={{ width: 18, height: 18 }}
            />
            <span style={{ fontWeight: 500 }}>Open to fully remote opportunities</span>
          </label>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, padding: 12, background: "#fff0f0", color: "#c00", borderRadius: 6 }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: 28, display: "flex", justifyContent: "space-between" }}>
        <button
          onClick={() => setStep((s) => Math.max(1, s - 1) as 1 | 2 | 3)}
          disabled={step === 1}
          style={{ padding: "10px 20px", borderRadius: 6, border: "1px solid #ddd", background: "white", cursor: step === 1 ? "not-allowed" : "pointer" }}
        >
          Back
        </button>
        {step < 3 ? (
          <button
            onClick={() => setStep((s) => Math.min(3, s + 1) as 1 | 2 | 3)}
            style={{ padding: "10px 24px", borderRadius: 6, border: "none", background: "#0070f3", color: "white", cursor: "pointer", fontWeight: 600 }}
          >
            Next →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading}
            style={{ padding: "10px 24px", borderRadius: 6, border: "none", background: "#0070f3", color: "white", cursor: loading ? "wait" : "pointer", fontWeight: 600 }}
          >
            {loading ? "Creating…" : "Get my feed →"}
          </button>
        )}
      </div>
    </div>
  );
}
