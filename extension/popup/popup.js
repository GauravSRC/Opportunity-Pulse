// Popup: shows the score breakdown for the active tab's listing and offers
// "save to OpportunityPulse". TODO(phase-5): query the active tab, request a
// score from the service worker, and render the component breakdown.

document.addEventListener("DOMContentLoaded", () => {
  const scoreEl = document.getElementById("score");
  const breakdownEl = document.getElementById("breakdown");
  // TODO(phase-5): chrome.tabs.query + chrome.runtime.sendMessage({type:"score"}).
  scoreEl.textContent = "—";
  breakdownEl.textContent = "TODO(phase-5): live score breakdown.";
});
