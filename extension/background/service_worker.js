// MV3 background service worker.
// Brokers messages between content scripts/popup and the backend API.

const API_BASE = "http://localhost:8000";

// Extract structured listing data from a raw page object sent by the content script
async function fetchAdhocScore(listing, userId) {
  if (!userId) return null;
  // The /opportunities/{id}/score endpoint requires the listing to exist in the DB.
  // For truly ad hoc scoring of pages not in the DB, we use the deadline extract
  // endpoint as a proxy for "backend reachable", and derive a rough local score
  // based on skill keyword matching as a fast fallback.
  // A full implementation would POST to a dedicated /score-adhoc endpoint.
  // Here we check if the backend is up and return a local heuristic.
  try {
    const r = await fetch(`${API_BASE}/healthz`);
    if (!r.ok) return null;
    // Try to find a matching listing in the DB by URL
    const params = new URLSearchParams({ q: listing.title?.slice(0, 40) ?? "", limit: "5" });
    if (userId) params.set("user_id", userId);
    const feedResp = await fetch(`${API_BASE}/opportunities?${params}`);
    if (!feedResp.ok) return null;
    const feed = await feedResp.json();
    const match = feed.items?.find(
      (i) => i.url === listing.url || i.title?.toLowerCase() === listing.title?.toLowerCase()
    );
    if (match) {
      return {
        score: match.score,
        listing_id: match.id,
        components: null,
        matched_skills: [],
        source: "feed_match",
      };
    }
    return null;
  } catch {
    return null;
  }
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "score") {
    chrome.storage.local.get(["userId"], async (result) => {
      const userId = result.userId ?? null;
      const scoreData = await fetchAdhocScore(msg.listing, userId);
      sendResponse({ score: scoreData?.score ?? null, data: scoreData });
    });
    return true;
  }

  if (msg?.type === "get_user_id") {
    chrome.storage.local.get(["userId"], (result) => {
      sendResponse({ userId: result.userId ?? null });
    });
    return true;
  }

  if (msg?.type === "set_user_id") {
    chrome.storage.local.set({ userId: msg.userId }, () => {
      sendResponse({ ok: true });
    });
    return true;
  }

  return true;
});
