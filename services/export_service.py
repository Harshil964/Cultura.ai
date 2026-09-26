"""Builds the 'Production Pack' zip: adapted screenplay, scene breakdown,
continuity report, character/costume bibles, and raw structured data —
everything the assignment's export screen promises, bundled together.

No LLM calls here — this is pure assembly of what earlier milestones
already produced and persisted.
"""
from __future__ import annotations

import io
import json
import zipfile

from database.repositories import project_repository as project_repo
from database.repositories import cultural_repository as cultural_repo
from database.repositories import adaptation_repository as adaptation_repo
from database.repositories import continuity_repository as continuity_repo


def build_production_pack(project_id: str) -> bytes:
    project = project_repo.get_project_summary(project_id)
    if project is None:
        raise ValueError(f"Unknown project_id {project_id}")

    plan = cultural_repo.get_plan(project_id)
    adapted_scenes = {s["scene_id"]: s for s in adaptation_repo.get_adapted_scenes(project_id)}
    issues = continuity_repo.get_issues(project_id)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("adapted_screenplay.md", _render_adapted_screenplay(project, adapted_scenes))
        zf.writestr("scene_breakdown.md", _render_scene_breakdown(project))
        zf.writestr("character_bible.md", _render_character_bible(project))
        zf.writestr("costume_bible.md", _render_costume_bible(project))
        zf.writestr("continuity_report.md", _render_continuity_report(issues))
        zf.writestr("cultural_plan.json", json.dumps(plan or {}, indent=2))
        zf.writestr(
            "structured_data.json",
            json.dumps(
                {
                    "project": {
                        "name": project["name"],
                        "culture": project["selected_culture"],
                        "region": project["selected_region"],
                        "setting": project["selected_setting"],
                        "script": project["selected_script"],
                    },
                    "scenes": project["scenes"],
                    "characters": project["characters"],
                    "locations": project["locations"],
                    "costumes": project["costumes"],
                    "props": project["props"],
                    "adapted_scenes": list(adapted_scenes.values()),
                    "continuity_issues": issues,
                },
                indent=2,
            ),
        )

    return buffer.getvalue()


def _render_adapted_screenplay(project: dict, adapted_scenes: dict) -> str:
    lines = [f"# {project['name']} — Adapted Screenplay", ""]
    for scene in project["scenes"]:
        lines.append(f"## {scene['scene_id']} — {scene['heading']}")
        adapted = adapted_scenes.get(scene["scene_id"])
        if adapted:
            lines.append(adapted["adapted_text"])
            if adapted["changes"]:
                lines.append("")
                lines.append("_Cultural changes:_")
                for c in adapted["changes"]:
                    lines.append(f"- **{c['aspect']}** — {c['explanation']}")
        else:
            lines.append(scene["raw_text"])
            lines.append("")
            lines.append("_(not yet adapted — original text shown)_")
        lines.append("")
    return "\n".join(lines)


def _render_scene_breakdown(project: dict) -> str:
    lines = ["# Scene Breakdown", ""]
    for s in project["scenes"]:
        lines.append(f"- **{s['scene_id']}** — {s['heading']} — {', '.join(s['character_names']) or 'no characters listed'}")
        lines.append(f"  {s['summary']}")
    return "\n".join(lines)


def _render_character_bible(project: dict) -> str:
    lines = ["# Character Bible", ""]
    for c in project["characters"]:
        lines.append(f"## {c['canonical_name']} ({c['character_id']})")
        lines.append(f"- Age: {c['age'] or '—'}")
        lines.append(f"- Role: {c['role'] or '—'}")
        if c["aliases"]:
            lines.append(f"- Aliases: {', '.join(c['aliases'])}")
        if c["relationships"]:
            lines.append(f"- Relationships: {', '.join(c['relationships'])}")
        lines.append("")
    return "\n".join(lines)


def _render_costume_bible(project: dict) -> str:
    lines = ["# Costume Bible", ""]
    if not project["costumes"]:
        lines.append("_No costumes extracted._")
    for co in project["costumes"]:
        lines.append(f"## {co['costume_id']}")
        lines.append(f"- Description: {co['description']}")
        lines.append(f"- Character: {co['character_id'] or '—'}")
        lines.append(f"- Scenes: {', '.join(co['scene_ids'])}")
        lines.append("")
    return "\n".join(lines)


def _render_continuity_report(issues: list[dict]) -> str:
    lines = ["# Continuity Report", ""]
    if not issues:
        lines.append("No continuity checks have been run yet, or no issues were found.")
        return "\n".join(lines)
    open_issues = [i for i in issues if i["status"] == "open"]
    lines.append(f"{len(open_issues)} open issue(s) out of {len(issues)} checked.")
    lines.append("")
    for i in issues:
        marker = "⚠ OPEN" if i["status"] == "open" else "✓ resolved"
        lines.append(f"- [{marker}] **{i['category']}** — {i['description']}")
    return "\n".join(lines)
