from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Agent routes — Sprint 8"})


@router.get("")
def list_agents():
    raise _NOT_IMPL


@router.post("", status_code=201)
def create_agent():
    raise _NOT_IMPL


@router.get("/{agent_id}")
def get_agent(agent_id: str):
    raise _NOT_IMPL


@router.patch("/{agent_id}")
def update_agent(agent_id: str):
    raise _NOT_IMPL


@router.delete("/{agent_id}")
def deactivate_agent(agent_id: str):
    raise _NOT_IMPL


@router.patch("/{agent_id}/position")
def update_agent_position(agent_id: str):
    raise _NOT_IMPL
