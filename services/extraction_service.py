"""Orchestrates the extraction milestone: run the agent, persist the
result, update project status. This is what Streamlit pages call —
they never touch the agent or repository directly.
"""
from __future__ import annotations

from agents.extraction_agent import extract, ExtractionAgentError
from database.repositories import project_repository as repo


def run_extraction(project_id: str, screenplay_text: str) -> tuple[bool, str | None]:
    """Returns (success, error_message)."""
    repo.set_extraction_status(project_id, "extracting")
    try:
        result = extract(screenplay_text)
    except ExtractionAgentError as e:
        repo.set_extraction_status(project_id, "failed")
        return False, str(e)

    repo.save_extraction_result(project_id, result)
    return True, None
