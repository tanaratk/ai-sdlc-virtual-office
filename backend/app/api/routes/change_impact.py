"""Change Impact API — POST /projects/{project_id}/change-impact."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.agents.change_impact_agent import ChangeImpactAgentRunner
from app.db.session import get_session
from app.db.models import Document, DocumentType, Project
from app.schemas.document import DocumentSummary

router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────────

class ChangeImpactRequest(BaseModel):
    change_description: str = Field(..., min_length=10)
    changed_requirement_ids: list[str] = Field(..., min_length=1)
    context_notes: str = ""


class ChangeImpactResponse(BaseModel):
    document_id: str
    title: str
    status: str
    message: str


# ── Route ──────────────────────────────────────────────────────────────────────

class ChangeImpactReportListResponse(BaseModel):
    items: list[DocumentSummary]


def _normalise_requirement_ids(ids: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in ids:
        value = raw.strip().upper()
        if not value:
            continue
        if value not in seen:
            cleaned.append(value)
            seen.add(value)
    return cleaned


@router.get(
    "/{project_id}/change-impact/reports",
    response_model=ChangeImpactReportListResponse,
    summary="List Change Impact reports",
)
def list_change_impact_reports(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> ChangeImpactReportListResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    docs = session.exec(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.change_impact_report,
        )
        .order_by(Document.created_at.desc())  # type: ignore[union-attr]
    ).all()
    return ChangeImpactReportListResponse(
        items=[DocumentSummary.model_validate(doc) for doc in docs]
    )


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
    session: Annotated[Session, Depends(get_session)],
) -> ChangeImpactResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    changed_ids = _normalise_requirement_ids(body.changed_requirement_ids)
    if not changed_ids:
        raise HTTPException(status_code=400, detail="At least one changed requirement ID is required")

    req_summary = session.exec(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.requirement_summary,
        )
        .limit(1)
    ).first()
    if not req_summary:
        raise HTTPException(
            status_code=400,
            detail="Run the Requirement Agent before triggering Change Impact analysis.",
        )

    runner = ChangeImpactAgentRunner(session)
    doc = runner.run(
        project_id=project_id,
        change_description=body.change_description,
        changed_requirement_ids=changed_ids,
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
