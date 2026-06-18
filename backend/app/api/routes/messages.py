from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Message routes — Sprint 8"})


@router.get("/{project_id}/messages")
def list_messages(project_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/messages", status_code=201)
def send_message(project_id: str):
    raise _NOT_IMPL
