from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Sprint routes — Sprint 8"})


@router.get("/{project_id}/sprints")
def list_sprints(project_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/sprints", status_code=201)
def create_sprint(project_id: str):
    raise _NOT_IMPL


@router.patch("/{project_id}/sprints/{sprint_id}")
def update_sprint(project_id: str, sprint_id: str):
    raise _NOT_IMPL
