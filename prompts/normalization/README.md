# Reserved: entity normalization agent

Not implemented yet. `agents/extraction_agent.py` already does basic
character de-duplication (aliases vs. new characters) as part of one LLM
call — this folder is for a **separate** normalization pass if that
inline de-duplication isn't reliable enough on a real screenplay (e.g.
merging "the old man" / "grandfather" / "Dada" across scenes with a
dedicated second LLM call or embedding-similarity check).

Add `system_prompt.py` here and a matching `agents/normalization_agent.py`
if you build this out.
