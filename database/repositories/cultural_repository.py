from __future__ import annotations

import uuid

from database.connection import get_session
from database.orm_models import Project, CulturalPlan
from schemas.cultural import CulturalPlanResult


def save_plan(project_id: str, result: CulturalPlanResult) -> None:
    """Replaces any existing plan wholesale (regenerate = start over)."""
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")

        existing = session.query(CulturalPlan).filter_by(project_id=project_id).one_or_none()
        if existing is not None:
            session.delete(existing)
            session.flush()

        confidence_summary = {
            "high": result.high_confidence_count,
            "needs_review": len(result.uncertain_decisions),
        }

        session.add(
            CulturalPlan(
                id=f"plan_{uuid.uuid4().hex[:10]}",
                project_id=project_id,
                verbal_adaptation=result.verbal_adaptation,
                non_verbal_adaptation=result.non_verbal_adaptation,
                visual_world=result.visual_world,
                uncertain_decisions=[d.model_dump() for d in result.uncertain_decisions],
                confidence_summary=confidence_summary,
                approval_status="awaiting_approval",
            )
        )
        project.cultural_plan_status = "awaiting_approval"


def get_plan(project_id: str) -> dict | None:
    with get_session() as session:
        plan = session.query(CulturalPlan).filter_by(project_id=project_id).one_or_none()
        if plan is None:
            return None
        return {
            "id": plan.id,
            "verbal_adaptation": plan.verbal_adaptation,
            "non_verbal_adaptation": plan.non_verbal_adaptation,
            "visual_world": plan.visual_world,
            "uncertain_decisions": plan.uncertain_decisions,
            "confidence_summary": plan.confidence_summary,
            "approval_status": plan.approval_status,
        }


def set_approval(project_id: str, approved: bool) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        plan = session.query(CulturalPlan).filter_by(project_id=project_id).one_or_none()
        if project is None or plan is None:
            raise ValueError(f"No plan to approve/reject for project {project_id}")
        plan.approval_status = "approved" if approved else "rejected"
        project.cultural_plan_status = plan.approval_status


def set_status(project_id: str, status: str) -> None:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Unknown project_id {project_id}")
        project.cultural_plan_status = status
