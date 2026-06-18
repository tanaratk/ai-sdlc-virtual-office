"""Change Impact API — POST /projects/{project_id}/change-impact."""
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.agents.change_impact_agent import ChangeImpactAgentRunner
from app.db.database import get_session
from app.db.models import Project

router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────────

class ChangeImpactRequest(BaseModel):
    change_description: str = Field(..., min_length=10)
    changed_requirement_ids: list[str] = Field(..., min_items=1)
    context_notes: str = ""


class ChangeImpactResponse(BaseModel):
    document_id: str
    title: str
    status: str
    message: str


# ── Route ──────────────────────────────────────────────────────────────────────

@router.post(
    "/{project_id}/change-impact",
    response_model=ChangeImpactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Change Impact Agent",
    description=(
        "Trigger the Change Impact Agent for a project. "
        "Provide a change description and the list of requirement IDs that changed. "
        "The agent reads all available project documents and returns a Change Impact Report."
    ),
)
def run_change_impact(
    project_id: uuid.UUID,
    body: ChangeImpactRequest,
    background_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_session)],
) -> ChangeImpactResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runner = ChangeImpactAgentRunner(session)
    doc = runner.run(
        project_id=project_id,
        change_description=body.change_description,
        changed_requirement_ids=body.changed_requirement_ids,
        context_notes=body.context_notes,
    )

    return ChangeImpactResponse(
        document_id=str(doc.id),
        title=doc.title,
        status=doc.status,
        message=(
            f"Change Impact Report created. "
            f"Review the report and decide which agents to re-run."
        ),
    )
