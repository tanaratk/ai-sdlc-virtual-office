import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.db.models import Agent
from app.schemas.agent import AgentResponse, AgentUpdate


class AgentService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self) -> list[AgentResponse]:
        agents = self.session.exec(
            select(Agent).where(Agent.is_active == True).order_by(Agent.name)
        ).all()
        return [AgentResponse.model_validate(a) for a in agents]

    def get(self, agent_id: uuid.UUID) -> AgentResponse:
        agent = self.session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Agent {agent_id} not found"})
        return AgentResponse.model_validate(agent)

    def update(self, agent_id: uuid.UUID, data: AgentUpdate) -> AgentResponse:
        agent = self.session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Agent {agent_id} not found"})
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(agent, field, value)
        agent.updated_at = datetime.now(UTC)
        self.session.add(agent)
        self.session.commit()
        self.session.refresh(agent)
        return AgentResponse.model_validate(agent)
