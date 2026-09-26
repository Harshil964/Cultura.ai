"""All DB reads/writes for a Project and its extracted entities live here.
Services/pages should never touch SQLAlchemy sessions directly — go through
this repository so the persistence layer can change without touching UI code.
"""
from __future__ import annotations

import uuid

from database.connection import get_session
from database.orm_models import Project, Scene, Character, Location, Costume, Prop
from schemas.adaptation import ExtractionResult


def create_project(name: str, source_filename: str | None, raw_text: str) -> str:
    project_id = f"proj_{uuid.uuid4().hex[:10]}"
    with get_session() as session:
        session.add(
            Project(
                id=project_id,
                name=name,
                source_filename=source_filename,
                raw_screenplay_text=raw_text,
                extraction_status="pending",
            )
        )
    return project_id


def set_cultural_target(project_id: str, culture: str, region: str, setting: str, script: str) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")
        project.selected_culture = culture
        project.selected_region = region
        project.selected_setting = setting
        project.selected_script = script


def set_extraction_status(project_id: str, status: str) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")
        project.extraction_status = status


def save_extraction_result(project_id: str, result: ExtractionResult) -> None:
    """Wipes and rewrites the derived-entity tables for this project.
    Extraction is meant to be re-run wholesale (e.g. re-analyze), not
    incrementally patched — that's what the later "edit" UI is for.
    """
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")

        for scene in project.scenes:
            session.delete(scene)
        for character in project.characters:
            session.delete(character)
        for location in project.locations:
            session.delete(location)
        for costume in project.costumes:
            session.delete(costume)
        for prop in project.props:
            session.delete(prop)
        session.flush()

        for s in result.scenes:
            session.add(
                Scene(
                    id=s.scene_id,
                    project_id=project_id,
                    scene_number=s.scene_number,
                    heading=s.heading,
                    location_name=s.location_name,
                    time_of_day=s.time_of_day,
                    interior_exterior=s.interior_exterior,
                    character_names=s.character_names,
                    prop_names=s.prop_names,
                    costume_notes=s.costume_notes,
                    summary=s.summary,
                    raw_text=s.raw_text,
                    review_status="ok",
                )
            )

        for c in result.characters:
            session.add(
                Character(
                    id=c.character_id,
                    project_id=project_id,
                    canonical_name=c.canonical_name,
                    aliases=c.aliases,
                    age=c.age,
                    role=c.role,
                    relationships=c.relationships,
                    first_scene_id=c.first_scene_id,
                )
            )

        for l in result.locations:
            session.add(Location(id=l.location_id, project_id=project_id, name=l.name, scene_ids=l.scene_ids))

        for co in result.costumes:
            session.add(
                Costume(
                    id=co.costume_id,
                    project_id=project_id,
                    description=co.description,
                    character_id=co.character_id,
                    scene_ids=co.scene_ids,
                )
            )

        for p in result.props:
            session.add(Prop(id=p.prop_id, project_id=project_id, name=p.name, scene_ids=p.scene_ids))

        project.extraction_status = "extracted"


def set_character_approved(character_id: str, approved: bool) -> None:
    with get_session() as session:
        character = session.get(Character, character_id)
        if character is None:
            raise ValueError(f"Unknown character_id {character_id}")
        character.approved = approved


def get_project_summary(project_id: str) -> dict | None:
    """Returns plain dicts (not ORM instances) so this is safe to use after
    the session that fetched it has closed — Streamlit pages hold this
    across reruns.
    """
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            return None
        return {
            "id": project.id,
            "name": project.name,
            "source_filename": project.source_filename,
            "extraction_status": project.extraction_status,
            "selected_culture": project.selected_culture,
            "selected_region": project.selected_region,
            "selected_setting": project.selected_setting,
            "selected_script": project.selected_script,
            "scenes": [
                {
                    "scene_id": s.id,
                    "scene_number": s.scene_number,
                    "heading": s.heading,
                    "location_name": s.location_name,
                    "time_of_day": s.time_of_day,
                    "interior_exterior": s.interior_exterior,
                    "character_names": s.character_names,
                    "prop_names": s.prop_names,
                    "costume_notes": s.costume_notes,
                    "summary": s.summary,
                    "raw_text": s.raw_text,
                    "review_status": s.review_status,
                }
                for s in sorted(project.scenes, key=lambda x: x.scene_number)
            ],
            "characters": [
                {
                    "character_id": c.id,
                    "canonical_name": c.canonical_name,
                    "aliases": c.aliases,
                    "age": c.age,
                    "role": c.role,
                    "relationships": c.relationships,
                    "first_scene_id": c.first_scene_id,
                    "approved": c.approved,
                }
                for c in project.characters
            ],
            "locations": [{"location_id": l.id, "name": l.name, "scene_ids": l.scene_ids} for l in project.locations],
            "costumes": [
                {
                    "costume_id": co.id,
                    "description": co.description,
                    "character_id": co.character_id,
                    "scene_ids": co.scene_ids,
                }
                for co in project.costumes
            ],
            "props": [{"prop_id": p.id, "name": p.name, "scene_ids": p.scene_ids} for p in project.props],
        }


def list_projects() -> list[dict]:
    with get_session() as session:
        projects = session.query(Project).order_by(Project.created_at.desc()).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "extraction_status": p.extraction_status,
                "created_at": p.created_at.isoformat(),
            }
            for p in projects
        ]
