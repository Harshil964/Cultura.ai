"""Calls the LLM once to turn raw screenplay text into a validated
ExtractionResult. No DB access here — extraction_service owns persistence.
"""
from __future__ import annotations

import json

from pydantic import ValidationError

from prompts.extraction.system_prompt import SYSTEM_PROMPT
from schemas.adaptation import ExtractionResult
from services.llm_client import complete_json

# Keep the schema-in-prompt small and hand-written rather than dumping the
# full Pydantic JSON schema — models follow a short annotated example more
# reliably than a raw json-schema block, and it's far cheaper on tokens.
RESPONSE_SHAPE = """{
  "scenes": [
    {
      "scene_number": 1,
      "scene_id": "SC01",
      "heading": "INT. COURTYARD - MORNING",
      "location_name": "Courtyard",
      "time_of_day": "MORNING",
      "interior_exterior": "INT",
      "character_names": ["Ravi", "Father"],
      "prop_names": ["letter"],
      "costume_notes": ["Ravi wears a torn kurta"],
      "summary": "Ravi confronts his father in the courtyard.",
      "raw_text": "<verbatim excerpt>"
    }
  ],
  "characters": [
    {
      "character_id": "CHAR_RAVI_001",
      "canonical_name": "Ravi",
      "aliases": ["Son", "the young man"],
      "age": "24",
      "role": "Son",
      "relationships": ["Father's son"],
      "first_scene_id": "SC01"
    }
  ],
  "locations": [{"location_id": "LOC_COURTYARD_001", "name": "Courtyard", "scene_ids": ["SC01"]}],
  "costumes": [{"costume_id": "COST_RAVI_001", "description": "Torn kurta", "character_id": "CHAR_RAVI_001", "scene_ids": ["SC01"]}],
  "props": [{"prop_id": "PROP_LETTER_001", "name": "letter", "scene_ids": ["SC01"]}],
  "warnings": ["Scene 2 had no explicit slugline; boundary was inferred."]
}"""


class ExtractionAgentError(RuntimeError):
    pass


def extract(screenplay_text: str) -> ExtractionResult:
    user_prompt = (
        "Convert the following screenplay into JSON matching exactly this shape "
        "(field names and structure, not the example values):\n\n"
        f"{RESPONSE_SHAPE}\n\n"
        "--- SCREENPLAY START ---\n"
        f"{screenplay_text}\n"
        "--- SCREENPLAY END ---"
    )

    raw_response = complete_json(SYSTEM_PROMPT, user_prompt)
    cleaned = _strip_code_fences(raw_response)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ExtractionAgentError(f"Model did not return valid JSON: {e}\n\nRaw response:\n{raw_response[:2000]}") from e

    try:
        return ExtractionResult.model_validate(payload)
    except ValidationError as e:
        raise ExtractionAgentError(f"Model JSON did not match the expected schema: {e}") from e


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
