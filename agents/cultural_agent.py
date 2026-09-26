from __future__ import annotations

import json

from pydantic import ValidationError

from prompts.cultural.system_prompt import SYSTEM_PROMPT
from schemas.cultural import CulturalPlanResult
from services.llm_client import complete_json


class CulturalAgentError(RuntimeError):
    pass


def generate_plan(
    scenes_summary: str,
    characters_summary: str,
    culture: str,
    region: str,
    setting: str,
    script: str,
) -> CulturalPlanResult:
    user_prompt = (
        f"Target culture: {culture}\nRegion: {region}\nSetting: {setting}\nScript: {script}\n\n"
        f"SCENES:\n{scenes_summary}\n\nCHARACTERS:\n{characters_summary}\n\n"
        "Produce the cultural adaptation plan as JSON, per your instructions."
    )

    raw_response = complete_json(SYSTEM_PROMPT, user_prompt)
    cleaned = _strip_code_fences(raw_response)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise CulturalAgentError(f"Model did not return valid JSON: {e}\n\nRaw response:\n{raw_response[:2000]}") from e

    try:
        return CulturalPlanResult.model_validate(payload)
    except ValidationError as e:
        raise CulturalAgentError(f"Model JSON did not match the expected schema: {e}") from e


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
