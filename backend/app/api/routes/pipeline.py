import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus, Project, User
from app.db.session import get_session
from app.schemas.pipeline import PipelineRunResponse, PipelineStepResponse
from app.services.pipeline_service import PipelineService
from app.worker.tasks import STEP_TASKS

router = APIRouter()


class _RejectBody(BaseModel):
    reason: str = "Rejected by user"


# ── Gate map ──────────────────────────────────────────────────────────────────
# step_name → next step name to create on approval (None = pipeline done)

_NEXT_STEP: dict[str, str | None] = {
    "gap_analysis":  "ba_documents",
    "ba_documents":  "sa_documents",
    "sa_documents":  "ux_documents",
    "ux_documents":  "dev_tasks",
    "dev_tasks":     "devops_tasks",
    "devops_tasks":  "test_cases",
    "test_cases":    "change_impact",
    "change_impact": "documentation",
    "documentation": "pm_summary",
    "pm_summary":    None,
}

# step_name → task key to dispatch on approval
_NEXT_TASK: dict[str, str] = {
    "gap_analysis":  "ba_documents",
    "ba_documents":  "sa_documents",
    "sa_documents":  "ux_documents",
    "ux_documents":  "dev_tasks",
    "dev_tasks":     "devops_tasks",
    "devops_tasks":  "test_cases",
    "test_cases":    "change_impact",
    "change_impact": "documentation",
    "documentation": "pm_summary",
}

# step_name → which task key retries that step
_RETRY_TASK: dict[str, str] = {
    "requirement_summary": "pipeline_start",
    "gap_analysis":        "pipeline_start",
    "ba_documents":        "ba_documents",
    "sa_documents":        "sa_documents",
    "ux_documents":        "ux_documents",
    "dev_tasks":           "dev_tasks",
    "devops_tasks":        "devops_tasks",
    "test_cases":          "test_cases",
    "change_impact":       "change_impact",
    "documentation":       "documentation",
    "pm_summary":          "pm_summary",
}


def _dispatch(task_key: str, run_id: uuid.UUID) -> None:
    task = STEP_TASKS.get(task_key)
    if task:
        task.delay(str(run_id))  # type: ignore[union-attr]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/{project_id}/pipeline/runs", response_model=PipelineRunResponse, status_code=201)
def start_pipeline_run(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    run = svc.create_run(project_id)
    _dispatch("pipeline_start", run.id)
    return PipelineRunResponse.model_validate(run)


@router.get("/{project_id}/pipeline/runs", response_model=list[PipelineRunResponse])
def list_pipeline_runs(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    return svc.list_runs(project_id)


@router.get("/{project_id}/pipeline/runs/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    return svc.get_run(project_id, run_id)


@router.get("/{project_id}/pipeline/runs/{run_id}/steps", response_model=list[PipelineStepResponse])
def list_pipeline_steps(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    return svc.list_steps(run_id)


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/approve", status_code=200)
def approve_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    run = session.exec(
        select(PipelineRun).where(
            PipelineRun.id == run_id,
            PipelineRun.project_id == project_id,
        )
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Run not found"})
    if run.status != PipelineRunStatus.waiting_for_user:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Run is {run.status.value}, not waiting_for_user"})

    step = session.get(PipelineStep, step_id)
    if not step or step.pipeline_run_id != run_id:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Step not found"})
    if step.step_name != run.current_step:
        raise HTTPException(status_code=400, detail={"error_code": "WRONG_STEP", "message": f"Step {step.step_name!r} is not the current gate ({run.current_step!r})"})

    next_step_name = _NEXT_STEP.get(step.step_name)

    if next_step_name is not None:
        next_step = PipelineStep(
            pipeline_run_id=run_id,
            step_name=next_step_name,
            status=PipelineStepStatus.pending,
        )
        session.add(next_step)
        run.status = PipelineRunStatus.running
        run.current_step = None
        session.commit()

        task_key = _NEXT_TASK.get(step.step_name)
        if task_key:
            _dispatch(task_key, run_id)

        return {"status": "approved", "next": next_step_name}
    else:
        run.status = PipelineRunStatus.completed
        run.completed_at = datetime.now(UTC)
        session.commit()
        return {"status": "approved", "run_id": str(run_id)}


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/reject", status_code=200)
def reject_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    body: _RejectBody,
    session: Session = Depends(get_session),
):
    run = session.exec(
        select(PipelineRun).where(
            PipelineRun.id == run_id,
            PipelineRun.project_id == project_id,
        )
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Run not found"})
    if run.status != PipelineRunStatus.waiting_for_user:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Run is {run.status.value}, not waiting_for_user"})

    step = session.get(PipelineStep, step_id)
    if not step or step.pipeline_run_id != run_id:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Step not found"})
    if step.step_name != run.current_step:
        raise HTTPException(status_code=400, detail={"error_code": "WRONG_STEP", "message": f"Step {step.step_name!r} is not the current gate ({run.current_step!r})"})

    run.status = PipelineRunStatus.failed
    step.status = PipelineStepStatus.failed
    step.error_message = body.reason[:2000]
    session.commit()
    return {"status": "rejected", "run_id": str(run_id)}


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun", status_code=200)
def rerun_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """Retry a failed pipeline step without creating a new run.

    Resets step + run status and re-dispatches the Celery task.
    """
    run = session.exec(
        select(PipelineRun).where(
            PipelineRun.id == run_id,
            PipelineRun.project_id == project_id,
        )
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Run not found"})
    if run.status != PipelineRunStatus.failed:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Run is {run.status.value} — only failed runs can be retried"})

    step = session.get(PipelineStep, step_id)
    if not step or step.pipeline_run_id != run_id:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Step not found"})
    if step.status != PipelineStepStatus.failed:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Step is {step.status.value} — only failed steps can be retried"})

    task_key = _RETRY_TASK.get(step.step_name)
    if not task_key:
        raise HTTPException(status_code=400, detail={"error_code": "NO_TASK", "message": f"No retry task defined for step {step.step_name!r}"})

    step.status = PipelineStepStatus.pending
    step.error_message = None
    step.started_at = None
    step.completed_at = None
    run.status = PipelineRunStatus.running
    run.current_step = None
    session.commit()

    _dispatch(task_key, run_id)
    return {"status": "retrying", "step": step.step_name, "task": task_key}


@router.post("/{project_id}/pipeline/runs/{run_id}/cancel", status_code=200)
def cancel_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Force-stop a running or waiting pipeline run.

    Marks the run as failed so the Celery task skips further work on
    its next DB read. Admin-only to prevent accidental cancellation.
    """
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail={"error_code": "FORBIDDEN", "message": "Only admin or manager can cancel a pipeline run"})

    run = session.exec(
        select(PipelineRun).where(
            PipelineRun.id == run_id,
            PipelineRun.project_id == project_id,
        )
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "Run not found"})
    if run.status not in (PipelineRunStatus.running, PipelineRunStatus.waiting_for_user):
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_STATE", "message": f"Run is already {run.status.value}"})

    # Mark any in-progress step as failed too
    in_progress = session.exec(
        select(PipelineStep).where(
            PipelineStep.pipeline_run_id == run_id,
            PipelineStep.status == PipelineStepStatus.running,
        )
    ).all()
    for step in in_progress:
        step.status = PipelineStepStatus.failed
        step.error_message = f"Cancelled by {current_user.email}"
        step.completed_at = datetime.now(UTC)

    run.status = PipelineRunStatus.failed
    run.completed_at = datetime.now(UTC)
    session.commit()
    return {"status": "cancelled", "run_id": str(run_id)}


