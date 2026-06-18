import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus
from app.db.session import engine, get_session
from app.schemas.pipeline import PipelineRunResponse, PipelineStepResponse
from app.services.pipeline_service import PipelineService

router = APIRouter()


class _RejectBody(BaseModel):
    reason: str = "Rejected by user"


def _run_pipeline_background(run_id: uuid.UUID) -> None:
    """Background task: Requirement Agent → Gap Analysis Agent (sequential)."""
    from app.agents.gap_analysis_agent import GapAnalysisAgentRunner
    from app.agents.requirement_agent import RequirementAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        RequirementAgentRunner(session).run(run_id)

    with _Session(engine) as session:
        GapAnalysisAgentRunner(session).run(run_id)


@router.post("/{project_id}/pipeline/runs", response_model=PipelineRunResponse, status_code=201)
def start_pipeline_run(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    run = svc.create_run(project_id)
    background_tasks.add_task(_run_pipeline_background, run.id)
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
    """Gate 1: human approves gap analysis. Sprint 10 will chain to BA Agent."""
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

    run.status = PipelineRunStatus.completed
    run.completed_at = datetime.utcnow()
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
    """Gate 1: human rejects gap analysis — marks run as failed."""
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

    run.status = PipelineRunStatus.failed
    step.status = PipelineStepStatus.failed
    step.error_message = body.reason[:2000]
    session.commit()
    return {"status": "rejected", "run_id": str(run_id)}


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun", status_code=501)
def rerun_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Step rerun — Sprint 10"})
