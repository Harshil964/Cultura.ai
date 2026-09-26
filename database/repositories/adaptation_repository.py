from __future__ import annotations

import uuid

from database.connection import get_session
from database.orm_models import Project, AdaptedScene
from schemas.adaptation_result import AdaptedSceneResult


def clear_adapted_scenes(project_id: str) -> None:
    with get_session() as session:
        session.query(AdaptedScene).filter_by(project_id=project_id).delete()


def save_adapted_scene(project_id: str, result: AdaptedSceneResult) -> None:
    with get_session() as session:
        existing = (
            session.query(AdaptedScene)
            .filter_by(project_id=project_id, scene_id=result.scene_id)
            .one_or_none()
        )
        if existing is not None:
            session.delete(existing)
            session.flush()

        session.add(
            AdaptedScene(
                id=f"adapt_{uuid.uuid4().hex[:10]}",
                project_id=project_id,
                scene_id=result.scene_id,
                adapted_text=result.adapted_text,
                changes=[c.model_dump() for c in result.changes],
            )
        )


def set_adaptation_status(project_id: str, status: str) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")
        project.adaptation_status = status


def get_adapted_scenes(project_id: str) -> list[dict]:
    with get_session() as session:
        rows = session.query(AdaptedScene).filter_by(project_id=project_id).all()
        return [
            {
                "scene_id": r.scene_id,
                "adapted_text": r.adapted_text,
                "changes": r.changes,
            }
            for r in rows
        ]
