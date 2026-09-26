from __future__ import annotations

import uuid

from database.connection import get_session
from database.orm_models import Project, ContinuityIssue


def clear_issues(project_id: str) -> None:
    with get_session() as session:
        session.query(ContinuityIssue).filter_by(project_id=project_id).delete()


def add_issue(project_id: str, category: str, description: str, affected_scene_ids: list[str]) -> None:
    with get_session() as session:
        session.add(
            ContinuityIssue(
                id=f"issue_{uuid.uuid4().hex[:10]}",
                project_id=project_id,
                category=category,
                description=description,
                affected_scene_ids=affected_scene_ids,
                status="open",
            )
        )


def set_status(project_id: str, status: str) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")
        project.continuity_status = status


def get_issues(project_id: str) -> list[dict]:
    with get_session() as session:
        rows = session.query(ContinuityIssue).filter_by(project_id=project_id).all()
        return [
            {
                "id": r.id,
                "category": r.category,
                "description": r.description,
                "affected_scene_ids": r.affected_scene_ids,
                "status": r.status,
            }
            for r in rows
        ]


def resolve_issue(issue_id: str) -> None:
    with get_session() as session:
        issue = session.get(ContinuityIssue, issue_id)
        if issue is not None:
            issue.status = "resolved"
