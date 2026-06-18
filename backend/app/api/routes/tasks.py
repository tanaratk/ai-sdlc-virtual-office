from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Task routes — Sprint 8"})


@router.get("/{project_id}/tasks")
def list_tasks(project_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/tasks/{task_id}")
def get_task(project_id: str, task_id: str):
    raise _NOT_IMPL


@router.patch("/{project_id}/tasks/{task_id}")
def update_task(project_id: str, task_id: str):
    raise _NOT_IMPL
