"""Thin, swappable wrapper around whichever LLM provider is configured.

Agents should never import openai/google.generativeai directly — they
call `complete_json(system, user)` and get back a raw string they parse
themselves into a Pydantic model. That keeps provider-switching to one
file and keeps the retry/error-handling logic in one place.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


class LLMConfigError(RuntimeError):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
def complete_json(system_prompt: str, user_prompt: str) -> str:
    """Returns the raw text of the model's response. Callers are
    responsible for stripping code fences and json.loads-ing it.
    Retries on transient provider errors (rate limits, timeouts).
    """
    if LLM_PROVIDER == "openai" or LLM_PROVIDER == "groq":
        return _complete_openai_compatible(system_prompt, user_prompt)
    if LLM_PROVIDER == "gemini":
        return _complete_gemini(system_prompt, user_prompt)
    raise LLMConfigError(f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Use openai, groq, or gemini.")


def _complete_openai_compatible(system_prompt: str, user_prompt: str) -> str:
    from openai import OpenAI

    if LLM_PROVIDER == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        base_url = "https://api.groq.com/openai/v1"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = None

    if not api_key:
        raise LLMConfigError(
            f"Missing API key for provider '{LLM_PROVIDER}'. Set it in your .env file."
        )

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def _complete_gemini(system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMConfigError("Missing GEMINI_API_KEY. Set it in your .env file.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=LLM_MODEL,
        system_instruction=system_prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(user_prompt)
    return response.text or ""
