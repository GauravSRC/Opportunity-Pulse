// Content script: injects a match-score badge onto a supported listing page.
// TODO(phase-5): extract the listing (title/org/description) from the DOM, POST
// it to the backend for an on-the-fly score, and render the badge.

(function injectBadge() {
  const badge = document.createElement("div");
  badge.id = "opportunitypulse-badge";
  badge.textContent = "OpportunityPulse: score pending";
  Object.assign(badge.style, {
    position: "fixed",
    bottom: "16px",
    right: "16px",
    zIndex: "2147483647",
    background: "#1a73e8",
    color: "#fff",
    padding: "8px 12px",
    borderRadius: "16px",
    font: "12px system-ui, sans-serif",
    boxShadow: "0 2px 8px rgba(0,0,0,.2)",
  });
  document.body.appendChild(badge);
  // TODO(phase-5): chrome.runtime.sendMessage({type:"score", listing}) -> update text.
})();
