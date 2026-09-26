from __future__ import annotations

import json

from pydantic import ValidationError

from prompts.adaptation.system_prompt import SYSTEM_PROMPT
from schemas.adaptation_result import AdaptedSceneResult
from services.llm_client import complete_json


class AdaptationAgentError(RuntimeError):
    pass


def adapt_scene(scene_id: str, original_text: str, plan_json: dict) -> AdaptedSceneResult:
    user_prompt = (
        f"APPROVED CULTURAL PLAN:\n{json.dumps(plan_json, indent=2)}\n\n"
        f"SCENE ({scene_id}) ORIGINAL TEXT:\n{original_text}\n\n"
        "Rewrite this scene per the plan, per your instructions."
    )

    raw_response = complete_json(SYSTEM_PROMPT, user_prompt)
    cleaned = _strip_code_fences(raw_response)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise AdaptationAgentError(
            f"Model did not return valid JSON for {scene_id}: {e}\n\nRaw response:\n{raw_response[:2000]}"
        ) from e

    payload.setdefault("scene_id", scene_id)

    try:
        return AdaptedSceneResult.model_validate(payload)
    except ValidationError as e:
        raise AdaptationAgentError(f"Model JSON for {scene_id} did not match the expected schema: {e}") from e


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
