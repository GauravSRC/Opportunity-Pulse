"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ProfileOut } from "@/lib/api";

const INTENTS = ["job", "internship", "research", "fellowship", "hackathon", "grant"];

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<ProfileOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const [headline, setHeadline] = useState("");
  const [skillsRaw, setSkillsRaw] = useState("");
  const [selectedIntents, setSelectedIntents] = useState<string[]>([]);
  const [locationsRaw, setLocationsRaw] = useState("");
  const [isRemoteOk, setIsRemoteOk] = useState(true);

  const profileId =
    typeof window !== "undefined" ? localStorage.getItem("profileId") ?? undefined : undefined;
  const userId =
    typeof window !== "undefined" ? localStorage.getItem("userId") ?? undefined : undefined;

  useEffect(() => {
    if (!profileId) { setLoading(false); return; }
    api.getProfile(profileId)
      .then((p) => {
        setProfile(p);
        setHeadline(p.headline ?? "");
        setSkillsRaw(p.skills.join(", "));
        setSelectedIntents(p.intents);
        setLocationsRaw(p.locations.join(", "));
        setIsRemoteOk(p.is_remote_ok);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [profileId]);

  function toggleIntent(intent: string) {
    setSelectedIntents((prev) =>
      prev.includes(intent) ? prev.filter((i) => i !== intent) : [...prev, intent]
    );
  }

  async function handleSave() {
    if (!profileId) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const skills = skillsRaw.split(",").map((s) => s.trim()).filter(Boolean);
      const locations = locationsRaw.split(",").map((s) => s.trim()).filter(Boolean);
      const updated = await api.updateProfile(profileId, {
        headline: headline || undefined,
        skills,
        intents: selectedIntents,
        locations,
        is_remote_ok: isRemoteOk,
      });
      setProfile(updated);
      setSaved(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("userId");
    localStorage.removeItem("profileId");
    router.push("/onboarding");
  }

  if (loading) return <p>Loading…</p>;

  if (!profileId || !userId) {
    return (
      <div>
        <h2>Settings</h2>
        <p style={{ color: "#666" }}>No profile found.</p>
        <a href="/onboarding" style={{ color: "#0070f3" }}>Set up your profile →</a>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <h2 style={{ marginTop: 0 }}>Profile Settings</h2>

      {profile && (
        <p style={{ fontSize: 13, color: "#888", marginBottom: 20 }}>
          Profile ID: {profile.id}
        </p>
      )}

      <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Headline</label>
      <input
        type="text"
        value={headline}
        onChange={(e) => { setHeadline(e.target.value); setSaved(false); }}
        placeholder="e.g. CS Student | ML & Backend"
        style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
      />

      <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Skills (comma-separated)</label>
      <input
        type="text"
        value={skillsRaw}
        onChange={(e) => { setSkillsRaw(e.target.value); setSaved(false); }}
        placeholder="Python, Machine Learning, React"
        style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
      />

      <label style={{ display: "block", fontWeight: 500, marginBottom: 10 }}>Opportunity types</label>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
        {INTENTS.map((intent) => (
          <button
            key={intent}
            onClick={() => { toggleIntent(intent); setSaved(false); }}
            style={{
              padding: "6px 16px",
              borderRadius: 20,
              border: "1.5px solid",
              borderColor: selectedIntents.includes(intent) ? "#0070f3" : "#ddd",
              background: selectedIntents.includes(intent) ? "#e8f0fe" : "white",
              color: selectedIntents.includes(intent) ? "#0070f3" : "#333",
              cursor: "pointer",
              textTransform: "capitalize",
            }}
          >
            {intent}
          </button>
        ))}
      </div>

      <label style={{ display: "block", fontWeight: 500, marginBottom: 6 }}>Locations (comma-separated)</label>
      <input
        type="text"
        value={locationsRaw}
        onChange={(e) => { setLocationsRaw(e.target.value); setSaved(false); }}
        placeholder="Remote, San Francisco"
        style={{ width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 6, marginBottom: 16, boxSizing: "border-box" }}
      />

      <label style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20, cursor: "pointer" }}>
        <input
          type="checkbox"
          checked={isRemoteOk}
          onChange={(e) => { setIsRemoteOk(e.target.checked); setSaved(false); }}
          style={{ width: 18, height: 18 }}
        />
        <span style={{ fontWeight: 500 }}>Open to remote opportunities</span>
      </label>

      {error && (
        <div style={{ marginBottom: 16, padding: 12, background: "#fff0f0", color: "#c00", borderRadius: 6 }}>
          {error}
        </div>
      )}

      <div style={{ display: "flex", gap: 12 }}>
        <button
          onClick={handleSave}
          disabled={saving}
          style={{ padding: "10px 24px", borderRadius: 6, border: "none", background: "#0070f3", color: "white", cursor: saving ? "wait" : "pointer", fontWeight: 600 }}
        >
          {saving ? "Saving…" : saved ? "✓ Saved" : "Save changes"}
        </button>
        <button
          onClick={handleLogout}
          style={{ padding: "10px 24px", borderRadius: 6, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Switch profile
        </button>
      </div>
    </div>
  );
}
