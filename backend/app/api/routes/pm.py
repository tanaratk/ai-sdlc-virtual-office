"""PM Agent API — POST /projects/{project_id}/pm-summary."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.agents.pm_agent import PMAgentRunner
from app.db.session import get_session
from app.db.models import Project

router = APIRouter()


class PMSummaryResponse(BaseModel):
    project_summary_id: str
    delivery_report_id: str
    project_summary_title: str
    delivery_report_title: str
    message: str


@router.post(
    "/{project_id}/pm-summary",
    response_model=PMSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run PM Agent — generate Project Summary and Delivery Report",
    description=(
        "Triggers the PM Agent (pipeline Step 10) to produce two final documents: "
        "an executive-level Project Summary and a data-driven Delivery Report. "
        "This is the final step in the 10-step AI-SDLC pipeline."
    ),
)
def run_pm_summary(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> PMSummaryResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runner = PMAgentRunner(session)
    try:
        ps_doc, dr_doc = runner.run(project_id=project_id, project_name=project.name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PMSummaryResponse(
        project_summary_id=str(ps_doc.id),
        delivery_report_id=str(dr_doc.id),
        project_summary_title=ps_doc.title,
        delivery_report_title=dr_doc.title,
        message=(
            "Pipeline Step 10 complete. Project Summary and Delivery Report are ready "
            "for review. Review and approve both documents to close this pipeline run."
        ),
    )
