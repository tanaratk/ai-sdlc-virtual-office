import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session, engine
from app.schemas.pipeline import PipelineRunResponse, PipelineStepResponse
from app.services.pipeline_service import PipelineService

router = APIRouter()


def _run_requirement_agent_background(run_id: uuid.UUID) -> None:
    """Sync background task — runs in FastAPI thread pool."""
    from app.agents.requirement_agent import RequirementAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        runner = RequirementAgentRunner(session)
        runner.run(run_id)


@router.post("/{project_id}/pipeline/runs", response_model=PipelineRunResponse, status_code=201)
def start_pipeline_run(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    svc = PipelineService(session)
    run = svc.create_run(project_id)
    background_tasks.add_task(_run_requirement_agent_background, run.id)
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
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Human-gate approve — Sprint 9"})


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/reject", status_code=200)
def reject_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Human-gate reject — Sprint 9"})


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun", status_code=200)
def rerun_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Step rerun — Sprint 9"})
