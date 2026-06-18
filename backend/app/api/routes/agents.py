import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.agent import AgentResponse
from app.services.agent_service import AgentService

router = APIRouter()


@router.get("", response_model=list[AgentResponse])
def list_agents(session: Session = Depends(get_session)):
    svc = AgentService(session)
    return svc.list_active()


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: uuid.UUID, session: Session = Depends(get_session)):
    svc = AgentService(session)
    return svc.get(agent_id)


@router.post("", status_code=501)
def create_agent():
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Agent create — Sprint 12"})


@router.patch("/{agent_id}", status_code=501)
def update_agent(agent_id: uuid.UUID):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Agent update — Sprint 12"})


@router.delete("/{agent_id}", status_code=501)
def deactivate_agent(agent_id: uuid.UUID):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Agent deactivate — Sprint 12"})


@router.patch("/{agent_id}/position", status_code=501)
def update_agent_position(agent_id: uuid.UUID):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Agent position — Sprint 14"})
