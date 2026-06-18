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


# ── Background tasks ───────────────────────────────────────────────────────────

def _run_pipeline_background(run_id: uuid.UUID) -> None:
    """Steps 1+2: Requirement Agent → Gap Analysis Agent (auto-chained)."""
    from app.agents.gap_analysis_agent import GapAnalysisAgentRunner
    from app.agents.requirement_agent import RequirementAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        RequirementAgentRunner(session).run(run_id)

    with _Session(engine) as session:
        GapAnalysisAgentRunner(session).run(run_id)


def _run_ba_agent_background(run_id: uuid.UUID) -> None:
    """Step 3: BA Agent — triggered by Gate 1 approval."""
    from app.agents.ba_agent import BAAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        BAAgentRunner(session).run(run_id)


def _run_sa_agent_background(run_id: uuid.UUID) -> None:
    """Step 4: SA Agent — triggered by Gate 2 approval."""
    from app.agents.sa_agent import SAAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        SAAgentRunner(session).run(run_id)


def _run_ux_agent_background(run_id: uuid.UUID) -> None:
    """Step 5: UX Agent — triggered by Gate 3 approval."""
    from app.agents.ux_agent import UXAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        UXAgentRunner(session).run(run_id)


def _run_dev_agent_background(run_id: uuid.UUID) -> None:
    """Step 6: Developer Agent — triggered by Gate 4 approval."""
    from app.agents.dev_agent import DevAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        DevAgentRunner(session).run(run_id)


def _run_qa_agent_background(run_id: uuid.UUID) -> None:
    """Step 7: QA Agent — triggered by Gate 5 approval."""
    from app.agents.qa_agent import QAAgentRunner
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        QAAgentRunner(session).run(run_id)


# ── Gate approval helpers ──────────────────────────────────────────────────────

# Maps step_name → next step to create on approval
_NEXT_STEP: dict[str, str | None] = {
    "gap_analysis": "ba_documents",   # Gate 1: approve → run BA Agent
    "ba_documents": "sa_documents",   # Gate 2: approve → run SA Agent
    "sa_documents": "ux_documents",   # Gate 3: approve → run UX Agent
    "ux_documents": "dev_tasks",      # Gate 4: approve → run Developer Agent
    "dev_tasks":    "test_cases",     # Gate 5: approve → run QA Agent
    "test_cases":   None,             # Gate 6: approve → pipeline completed
}

_NEXT_BACKGROUND: dict[str, object] = {
    "ba_documents": _run_ba_agent_background,
    "sa_documents": _run_sa_agent_background,
    "ux_documents": _run_ux_agent_background,
    "dev_tasks":    _run_dev_agent_background,
    "test_cases":   _run_qa_agent_background,
}


# ── Routes ─────────────────────────────────────────────────────────────────────

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
    background_tasks: BackgroundTasks,
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
        # Create next step and fire its background agent
        next_step = PipelineStep(
            pipeline_run_id=run_id,
            step_name=next_step_name,
            status=PipelineStepStatus.pending,
        )
        session.add(next_step)
        run.status = PipelineRunStatus.running
        run.current_step = None
        session.commit()
        background_fn = _NEXT_BACKGROUND.get(next_step_name)
        if background_fn:
            background_tasks.add_task(background_fn, run_id)
        return {"status": "approved", "next": next_step_name}
    else:
        # Gate 6 (test_cases) — pipeline complete
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


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun", status_code=501)
def rerun_step(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    step_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Step rerun — Sprint 14"})
