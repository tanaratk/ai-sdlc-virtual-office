"""Admin-only endpoints that span multiple projects."""
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus, Project, User
from app.db.session import get_session

router = APIRouter()


@router.get("/pipeline/active")
def list_active_runs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all pipeline runs currently running or waiting across every project."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail={"error_code": "FORBIDDEN", "message": "Admin or manager only"})

    runs = session.exec(
        select(PipelineRun).where(
            PipelineRun.status.in_([PipelineRunStatus.running, PipelineRunStatus.waiting_for_user])
        ).order_by(PipelineRun.started_at.desc())
    ).all()

    result = []
    for run in runs:
        project = session.get(Project, run.project_id)
        steps = session.exec(
            select(PipelineStep).where(PipelineStep.pipeline_run_id == run.id)
        ).all()
        latest_step = max(
            (s for s in steps if s.status.value in ("running", "pending")),
            key=lambda s: s.started_at or datetime.min.replace(tzinfo=UTC),
            default=steps[-1] if steps else None,
        )
        result.append({
            "run_id": str(run.id),
            "project_id": str(run.project_id),
            "project_name": project.name if project else "Unknown",
            "status": run.status.value,
            "current_step": run.current_step,
            "active_step": latest_step.step_name if latest_step else None,
            "active_step_status": latest_step.status.value if latest_step else None,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "step_count": len(steps),
        })
    return {"active_runs": result, "total": len(result)}


@router.post("/pipeline/runs/{run_id}/cancel")
def cancel_run_admin(
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Force-cancel any active pipeline run (admin/manager only)."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail={"error_code": "FORBIDDEN", "message": "Admin or manager only"})

    run = session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Run not found"})
    if run.status not in (PipelineRunStatus.running, PipelineRunStatus.waiting_for_user):
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Run is already {run.status.value}"})

    in_progress = session.exec(
        select(PipelineStep).where(
            PipelineStep.pipeline_run_id == run_id,
            PipelineStep.status.in_([PipelineStepStatus.running, PipelineStepStatus.pending]),
        )
    ).all()
    for step in in_progress:
        step.status = PipelineStepStatus.failed
        step.error_message = f"Cancelled by {current_user.email}"
        step.completed_at = datetime.now(UTC)

    run.status = PipelineRunStatus.failed
    run.completed_at = datetime.now(UTC)
    session.commit()
    return {"status": "cancelled", "run_id": str(run_id), "project_id": str(run.project_id)}
