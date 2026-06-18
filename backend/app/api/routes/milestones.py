from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Milestone routes — Sprint 8"})


@router.get("/{project_id}/milestones")
def list_milestones(project_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/milestones", status_code=201)
def create_milestone(project_id: str):
    raise _NOT_IMPL


@router.patch("/{project_id}/milestones/{milestone_id}")
def update_milestone(project_id: str, milestone_id: str):
    raise _NOT_IMPL
