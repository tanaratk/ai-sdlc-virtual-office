import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.db.models import (
    PipelineRun,
    PipelineRunStatus,
    PipelineStep,
    PipelineStepStatus,
    Project,
    RequirementInput,
)
from app.schemas.pipeline import PipelineRunResponse, PipelineStepResponse


class PipelineService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, project_id: uuid.UUID) -> PipelineRun:
        project = self.session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Project {project_id} not found"})

        has_inputs = self.session.exec(
            select(RequirementInput).where(RequirementInput.project_id == project_id).limit(1)
        ).first()
        if not has_inputs:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "NO_INPUTS", "message": "No requirement inputs found. Upload at least one requirement before running the pipeline."},
            )

        active_run = self.session.exec(
            select(PipelineRun).where(
                PipelineRun.project_id == project_id,
                PipelineRun.status.in_([  # type: ignore[union-attr]
                    PipelineRunStatus.pending,
                    PipelineRunStatus.running,
                    PipelineRunStatus.waiting_for_user,
                ]),
            ).limit(1)
        ).first()
        if active_run:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "RUN_IN_PROGRESS",
                    "message": f"A pipeline run is already active (status: {active_run.status.value}). Wait for it to complete or fail before starting a new one.",
                },
            )

        run = PipelineRun(project_id=project_id, status=PipelineRunStatus.pending)
        self.session.add(run)
        self.session.flush()

        step = PipelineStep(
            pipeline_run_id=run.id,
            step_name="requirement_summary",
            status=PipelineStepStatus.pending,
        )
        self.session.add(step)
        self.session.commit()
        self.session.refresh(run)
        return run

    def list_runs(self, project_id: uuid.UUID) -> list[PipelineRunResponse]:
        runs = self.session.exec(
            select(PipelineRun)
            .where(PipelineRun.project_id == project_id)
            .order_by(PipelineRun.created_at.desc())
        ).all()
        return [PipelineRunResponse.model_validate(r) for r in runs]

    def get_run(self, project_id: uuid.UUID, run_id: uuid.UUID) -> PipelineRunResponse:
        run = self.session.exec(
            select(PipelineRun).where(
                PipelineRun.id == run_id,
                PipelineRun.project_id == project_id,
            )
        ).first()
        if not run:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Run {run_id} not found"})
        return PipelineRunResponse.model_validate(run)

    def list_steps(self, run_id: uuid.UUID) -> list[PipelineStepResponse]:
        steps = self.session.exec(
            select(PipelineStep).where(PipelineStep.pipeline_run_id == run_id)
        ).all()
        return [PipelineStepResponse.model_validate(s) for s in steps]
