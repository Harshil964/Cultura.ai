"""Deliberately rule-based, not LLM-based: continuity checks need to be
deterministic and explainable ("why did this flag?"), which a rule engine
gives you for free and an LLM call would only approximate.

Returns an overall consistency score (0-100) the way the Continuity
Control Center mockup wants: a big percentage plus a per-category checklist.
"""
from __future__ import annotations

from database.repositories import project_repository as project_repo
from database.repositories import continuity_repository as continuity_repo

CATEGORIES = ["character", "location", "costume", "prop", "scene_order"]


def run_continuity_check(project_id: str) -> dict:
    project = project_repo.get_project_summary(project_id)
    if project is None:
        raise ValueError(f"Unknown project_id {project_id}")

    continuity_repo.clear_issues(project_id)

    known_character_names = _build_known_names(project["characters"])
    known_location_names = {loc["name"].strip().lower() for loc in project["locations"]}

    total_checks = 0
    failed_checks = 0

    # --- Character identity consistency ---
    for scene in project["scenes"]:
        for name in scene["character_names"]:
            total_checks += 1
            if name.strip().lower() not in known_character_names:
                failed_checks += 1
                continuity_repo.add_issue(
                    project_id,
                    "character",
                    f"'{name}' appears in {scene['scene_id']} but doesn't match any known character "
                    f"or alias — possible unresolved identity.",
                    [scene["scene_id"]],
                )

    # --- Location consistency ---
    for scene in project["scenes"]:
        total_checks += 1
        if scene["location_name"].strip().lower() not in known_location_names:
            failed_checks += 1
            continuity_repo.add_issue(
                project_id,
                "location",
                f"{scene['scene_id']} is set at '{scene['location_name']}', which isn't in the "
                f"registered locations list.",
                [scene["scene_id"]],
            )

    # --- Prop continuity: a prop carried by a character shouldn't silently
    #     vanish in the character's very next scene without explanation. ---
    scenes_sorted = sorted(project["scenes"], key=lambda s: s["scene_number"])
    prop_last_seen: dict[str, tuple[str, set[str]]] = {}  # prop -> (scene_id, character set)

    for scene in scenes_sorted:
        total_checks += 1
        current_chars = {c.strip().lower() for c in scene["character_names"]}
        current_props = {p.strip().lower() for p in scene["prop_names"]}
        dropped = False

        for prop, (last_scene_id, last_chars) in list(prop_last_seen.items()):
            shared_chars = last_chars & current_chars
            if shared_chars and prop not in current_props:
                dropped = True
                continuity_repo.add_issue(
                    project_id,
                    "prop",
                    f"'{prop}' was present with {', '.join(sorted(shared_chars))} in {last_scene_id} "
                    f"but is missing in {scene['scene_id']}.",
                    [last_scene_id, scene["scene_id"]],
                )

        if dropped:
            failed_checks += 1

        for prop in current_props:
            prop_last_seen[prop] = (scene["scene_id"], current_chars)

    # --- Scene order: numbers should be contiguous starting at 1, no dupes ---
    total_checks += 1
    numbers = [s["scene_number"] for s in scenes_sorted]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        failed_checks += 1
        continuity_repo.add_issue(
            project_id,
            "scene_order",
            f"Scene numbers are not a clean 1..N sequence: got {numbers}.",
            [s["scene_id"] for s in scenes_sorted],
        )

    consistency_pct = round(100 * (total_checks - failed_checks) / total_checks) if total_checks else 100
    continuity_repo.set_status(project_id, "checked")

    return {
        "consistency_pct": consistency_pct,
        "total_checks": total_checks,
        "failed_checks": failed_checks,
    }


def _build_known_names(characters: list[dict]) -> set[str]:
    names: set[str] = set()
    for c in characters:
        names.add(c["canonical_name"].strip().lower())
        for alias in c["aliases"]:
            names.add(alias.strip().lower())
    return names
