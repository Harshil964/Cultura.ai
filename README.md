# Cultura AI — Cultural Screenplay & Visual Adaptation Studio

Full pipeline is now wired end-to-end:

**Upload → Extraction → Characters → Cultural Plan (human approval gate) →
Adaptation → Visual Studio (stubbed) → Continuity → Export**

A screenplay (PDF/DOCX/TXT or pasted text) goes in; a structured breakdown
comes out; a cultural adaptation plan is generated and must be **approved by
a human before adaptation is allowed to run** (enforced in code, not just
UI — see `AdaptationNotAllowed`); adapted dialogue is shown side-by-side
with the original with per-line change reasoning; a rule-based continuity
engine flags dropped props/unknown characters/unregistered locations across
scenes; everything bundles into one downloadable production pack.

Verified end-to-end with a mocked-LLM smoke test covering all 5 stages,
including confirming the approval gate actually blocks adaptation and the
continuity engine catches a deliberately-planted dropped prop.

## 1. Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env:
#   - set LLM_PROVIDER (openai / groq / gemini) and the matching API key
#   - DATABASE_URL is optional — if you skip it, a local cultura.db
#     SQLite file is created automatically, no Postgres needed
```

## 2. Run

```bash
streamlit run app.py
```

Opens at http://localhost:8501. Click **＋ New Adaptation**, upload a
screenplay (or paste text), pick a cultural target, and hit **Analyze
Screenplay**.

## 3. How it's wired

```
Streamlit page (pages/01_Upload.py)
        │
        ▼
services/document_service.py   — PDF/DOCX/TXT → plain text
        │
        ▼
services/extraction_service.py — orchestrates the milestone
        │
        ▼
agents/extraction_agent.py     — builds the prompt, calls the LLM,
        │                          validates the response against
        │                          schemas/adaptation.py (Pydantic)
        ▼
services/llm_client.py         — provider-agnostic call (OpenAI/Groq/Gemini)
        │
        ▼
database/repositories/project_repository.py — persists to SQLAlchemy
        │
        ▼
pages/02_Extraction.py         — reads it back, renders tabs/tables/cards
```

Nothing in `pages/` talks to the database or the LLM directly — it only
calls `services/`. That's what makes it safe to swap Streamlit for another
frontend later without touching the AI logic.

## 4. Known limitations

- Character "Edit" / "Merge" buttons, and the Cultural Plan's "Edit" button,
  are placeholders — re-running Analyze Screenplay / Regenerate Plan is
  currently the only fix path. Inline editing is a fast follow.
- **Visual Studio (image generation) is stubbed, not implemented.**
  `services/visual_service.py` defines the interface
  (`generate_image(prompt) -> bytes`) the page already calls — plug in
  OpenAI Images / Gemini / Stability there and the page lights up with no
  other changes needed.
- Continuity's "Regenerate Scene" button is disabled — wire it to call
  `agents/adaptation_agent.adapt_scene` for just the affected scene_id.
- `review_status` on scenes is stored but nothing sets it to `needs_review`
  yet; wire that up once you decide what should trigger it (e.g. the LLM's
  own `warnings` list, or a rule like "scene has no characters").
- The continuity engine's prop-drop heuristic (flag when two scenes share a
  character but a prop seen with them vanishes) is intentionally simple —
  tune it per screenplay if it's too noisy or too lax.

