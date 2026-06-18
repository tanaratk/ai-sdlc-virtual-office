"""Documentation API — POST /projects/{project_id}/compile-docs."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.agents.documentation_agent import DocumentationAgentRunner
from app.db.database import get_session
from app.db.models import Project

router = APIRouter()


class CompileDocsResponse(BaseModel):
    document_id: str
    title: str
    status: str
    message: str


@router.post(
    "/{project_id}/compile-docs",
    response_model=CompileDocsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compile all project documents into one bundle",
    description=(
        "Triggers the Documentation Agent to collect all available project documents "
        "and compile them into a single Compiled Document Set with an executive summary, "
        "table of contents, and document index."
    ),
)
def compile_docs(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> CompileDocsResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runner = DocumentationAgentRunner(session)
    try:
        doc = runner.run(project_id=project_id, project_name=project.name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return CompileDocsResponse(
        document_id=str(doc.id),
        title=doc.title,
        status=doc.status,
        message=(
            f"Compiled Document Set created. "
            f"Review the bundle in Documents and approve when ready."
        ),
    )
