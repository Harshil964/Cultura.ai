# Reserved: structured cultural reference data

Currently unused — `agents/cultural_agent.py` relies entirely on the LLM's
own knowledge of the target culture, passed via prompt (culture/region/
setting/script strings only).

If you want more consistent, fact-checked cultural output, put structured
reference data here (e.g. `kinship_terms.json`, `wardrobe.json`,
`dialect_notes.json`) and load it into the prompt in
`services/cultural_service.run_cultural_planning()` alongside the scene/
character summaries — that's the "optional retrieval" layer mentioned in
the original architecture notes.
