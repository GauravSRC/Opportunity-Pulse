# OpportunityPulse Chrome Extension (MV3)

Shows your live match score on supported opportunity listing pages and lets you
save a listing to your account.

## Load (unpacked)

1. Open `chrome://extensions`, enable **Developer mode**.
2. **Load unpacked** → select this `extension/` directory.
3. Visit a supported listing page (e.g. a Greenhouse/Lever board) to see the
   badge; click the toolbar icon for the popup.

## Structure

- `manifest.json` — MV3 manifest (permissions, content scripts, background).
- `content/content.js` — injects the match-score badge.
- `background/service_worker.js` — brokers API calls + holds auth token.
- `popup/` — popup UI with score breakdown + save action.

Phase-0 scaffold: scoring/auth are `TODO(phase-5)`. The badge renders so the
end-to-end wiring is visible.
