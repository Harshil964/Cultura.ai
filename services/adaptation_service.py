from __future__ import annotations

from agents.adaptation_agent import adapt_scene, AdaptationAgentError
from database.repositories import adaptation_repository as adapt_repo
from database.repositories import cultural_repository as cultural_repo
from database.repositories import project_repository as project_repo


class AdaptationNotAllowed(RuntimeError):
    pass


def run_adaptation(project_id: str) -> tuple[bool, str | None]:
    plan = cultural_repo.get_plan(project_id)
    if plan is None or plan["approval_status"] != "approved":
        raise AdaptationNotAllowed(
            "Adaptation requires an approved cultural plan. Approve the plan first."
        )

    project = project_repo.get_project_summary(project_id)
    if project is None:
        return False, "Unknown project"

    adapt_repo.set_adaptation_status(project_id, "adapting")
    adapt_repo.clear_adapted_scenes(project_id)

    plan_json = {
        "verbal_adaptation": plan["verbal_adaptation"],
        "non_verbal_adaptation": plan["non_verbal_adaptation"],
        "visual_world": plan["visual_world"],
    }

    errors: list[str] = []
    for scene in project["scenes"]:
        try:
            result = adapt_scene(scene["scene_id"], scene["raw_text"], plan_json)
            adapt_repo.save_adapted_scene(project_id, result)
        except AdaptationAgentError as e:
            errors.append(str(e))

    if errors:
        adapt_repo.set_adaptation_status(project_id, "failed")
        return False, "; ".join(errors)

    adapt_repo.set_adaptation_status(project_id, "adapted")
    return True, None
