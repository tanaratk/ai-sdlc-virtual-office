from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Activity routes — Sprint 8"})


@router.get("/{project_id}/activity")
def get_activity(project_id: str):
    raise _NOT_IMPL
