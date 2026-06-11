// Popup: shows match score for the active tab and allows saving the listing.

const API_BASE = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  const scoreEl = document.getElementById("score");
  const breakdownEl = document.getElementById("breakdown");
  const saveBtn = document.getElementById("save");
  const userIdInput = document.getElementById("user-id");
  const userIdSaveBtn = document.getElementById("user-id-save");
  const statusEl = document.getElementById("status");

  // Load stored userId
  chrome.runtime.sendMessage({ type: "get_user_id" }, (r) => {
    if (r?.userId && userIdInput) userIdInput.value = r.userId;
  });

  if (userIdSaveBtn) {
    userIdSaveBtn.addEventListener("click", () => {
      const uid = userIdInput?.value?.trim();
      if (!uid) return;
      chrome.runtime.sendMessage({ type: "set_user_id", userId: uid }, () => {
        if (statusEl) { statusEl.textContent = "Saved!"; setTimeout(() => { statusEl.textContent = ""; }, 1500); }
        loadScore();
      });
    });
  }

  function loadScore() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab?.url || !tab.url.startsWith("http")) {
        scoreEl.textContent = "—";
        breakdownEl.textContent = "Open a supported listing page.";
        return;
      }

      breakdownEl.textContent = "Checking…";

      // Ask the content script for listing data via executeScript
      chrome.scripting
        .executeScript({
          target: { tabId: tab.id },
          func: () => ({
            title: document.querySelector("h1")?.innerText?.trim() || document.title,
            url: window.location.href.split("?")[0],
          }),
        })
        .then((results) => {
          const listing = results?.[0]?.result;
          if (!listing) { breakdownEl.textContent = "Could not extract listing."; return; }

          chrome.runtime.sendMessage({ type: "score", listing }, (response) => {
            const { score, data } = response ?? {};
            if (score !== null && score !== undefined) {
              const pct = Math.round(score * 100);
              scoreEl.textContent = `${pct}%`;
              breakdownEl.textContent = data?.matched_skills?.length
                ? `Matched: ${data.matched_skills.slice(0, 4).join(", ")}`
                : "Score available. Open detail for explanation.";
              saveBtn.disabled = false;
              saveBtn.dataset.listingId = data?.listing_id ?? "";
            } else {
              scoreEl.textContent = "—";
              breakdownEl.textContent = "Not in your feed yet. Run the pipeline or check your profile.";
            }
          });
        })
        .catch(() => {
          breakdownEl.textContent = "Cannot access this page.";
        });
    });
  }

  loadScore();

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      const id = saveBtn.dataset.listingId;
      if (id) window.open(`http://localhost:3000/opportunity/${id}`, "_blank");
    });
  }
});
