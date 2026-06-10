// MV3 background service worker.
// Brokers messages between content scripts/popup and the backend API, and holds
// the auth token in chrome.storage. TODO(phase-5): implement scoring + auth.

const API_BASE = "http://localhost:8000";

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "score") {
    // TODO(phase-5): POST msg.listing to `${API_BASE}/opportunities/score-adhoc`
    // and return {score, components}.
    sendResponse({ score: null, note: "TODO(phase-5)" });
  }
  return true; // keep the message channel open for async response
});
