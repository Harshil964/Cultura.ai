# Generated output — currently unused on disk

Reserved for the original architecture's plan to write generated assets
to disk (`generated/characters/`, `generated/costumes/`, `generated/scenes/`,
`generated/reports/`). The current build does NOT write here:

- Visual Studio (`services/visual_service.py`) is stubbed — no images are
  generated yet, so nothing lands in `characters/` / `costumes/` / `scenes/`.
- The production pack (`services/export_service.py`) builds its zip
  **in memory** and streams it via Streamlit's download button — it never
  touches `reports/`.

If you'd rather have the app persist these to disk (e.g. so re-opening a
project doesn't require re-downloading), that's a small change: write the
bytes/images into the matching subfolder here, keyed by project_id, instead
of returning them directly.
