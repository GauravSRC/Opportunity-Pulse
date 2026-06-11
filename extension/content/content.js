// Content script: injects a match-score badge onto supported listing pages.
// Extracts title/org from the DOM, requests a score from the service worker,
// and renders the badge with the result.

(function injectBadge() {
  "use strict";

  // Don't inject twice
  if (document.getElementById("opportunitypulse-badge")) return;

  // ── Extract listing metadata from the page ─────────────────────────────────

  function extractListing() {
    const title =
      document.querySelector("h1")?.innerText?.trim() ||
      document.title?.split("|")[0]?.trim() ||
      document.title;

    // Greenhouse
    const ghOrg = document.querySelector(".company-name, .job__company-name, .board-title")?.innerText?.trim();
    // Lever
    const levOrg = document.querySelector(".main-header-employer, .company-name")?.innerText?.trim();

    const org = ghOrg || levOrg || window.location.hostname;
    const url = window.location.href.split("?")[0];
    const description = document.querySelector(
      ".job-description, .content-wrapper, .posting-description, article"
    )?.innerText?.slice(0, 500) ?? "";

    return { title, org, url, description };
  }

  // ── Badge ─────────────────────────────────────────────────────────────────

  const badge = document.createElement("div");
  badge.id = "opportunitypulse-badge";
  Object.assign(badge.style, {
    position: "fixed",
    bottom: "16px",
    right: "16px",
    zIndex: "2147483647",
    background: "#1a73e8",
    color: "#fff",
    padding: "10px 16px",
    borderRadius: "20px",
    font: "13px system-ui, sans-serif",
    boxShadow: "0 2px 8px rgba(0,0,0,.25)",
    cursor: "pointer",
    userSelect: "none",
    transition: "transform 0.15s",
    maxWidth: "220px",
  });
  badge.textContent = "⚡ OpportunityPulse: scoring…";
  document.body.appendChild(badge);

  // ── Request score ─────────────────────────────────────────────────────────

  const listing = extractListing();

  chrome.runtime.sendMessage({ type: "score", listing }, (response) => {
    if (chrome.runtime.lastError) {
      badge.textContent = "⚡ OpportunityPulse (offline)";
      badge.style.background = "#888";
      return;
    }
    const { score, data } = response ?? {};
    if (score !== null && score !== undefined) {
      const pct = Math.round(score * 100);
      const color = pct >= 70 ? "#137333" : pct >= 40 ? "#f09300" : "#666";
      badge.style.background = color;
      badge.textContent = `⚡ ${pct}% match`;
      badge.title = `OpportunityPulse match score for "${listing.title}"`;
      if (data?.matched_skills?.length) {
        badge.title += `\nMatched: ${data.matched_skills.join(", ")}`;
      }
    } else {
      badge.style.background = "#555";
      badge.textContent = "⚡ OpportunityPulse";
      badge.title = "No score yet — set up your profile at localhost:3000";
    }
  });

  // Click opens the web app
  badge.addEventListener("click", () => {
    window.open(`http://localhost:3000/feed`, "_blank");
  });
})();
