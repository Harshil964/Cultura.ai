from __future__ import annotations

from agents.cultural_agent import generate_plan, CulturalAgentError
from database.repositories import cultural_repository as repo
from database.repositories import project_repository as project_repo


def run_cultural_planning(project_id: str) -> tuple[bool, str | None]:
    project = project_repo.get_project_summary(project_id)
    if project is None:
        return False, "Unknown project"
    if not project["scenes"]:
        return False, "No extracted scenes to plan from — run Extraction first."

    repo.set_status(project_id, "generating")

    scenes_summary = "\n".join(
        f"{s['scene_id']} ({s['location_name']}, {s['time_of_day']}): {s['summary']}" for s in project["scenes"]
    )
    characters_summary = "\n".join(
        f"{c['canonical_name']} ({c['role'] or 'role unknown'}, age {c['age'] or '?'})"
        for c in project["characters"]
    )

    try:
        result = generate_plan(
            scenes_summary=scenes_summary,
            characters_summary=characters_summary,
            culture=project["selected_culture"] or "Unspecified",
            region=project["selected_region"] or "Unspecified",
            setting=project["selected_setting"] or "Unspecified",
            script=project["selected_script"] or "Unspecified",
        )
    except CulturalAgentError as e:
        repo.set_status(project_id, "failed")
        return False, str(e)

    repo.save_plan(project_id, result)
    return True, None
