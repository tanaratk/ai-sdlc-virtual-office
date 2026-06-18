from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Pipeline routes — Sprint 8"})


@router.post("/{project_id}/pipeline/runs", status_code=201)
def start_pipeline_run(project_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/pipeline/runs")
def list_pipeline_runs(project_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/pipeline/runs/{run_id}")
def get_pipeline_run(project_id: str, run_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/pipeline/runs/{run_id}/steps")
def list_pipeline_steps(project_id: str, run_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/approve")
def approve_step(project_id: str, run_id: str, step_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/reject")
def reject_step(project_id: str, run_id: str, step_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun")
def rerun_step(project_id: str, run_id: str, step_id: str):
    raise _NOT_IMPL
