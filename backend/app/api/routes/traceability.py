import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.traceability import (
    AutoLinkResult,
    TraceabilityLinkCreate,
    TraceabilityLinkResponse,
    TraceabilityMatrix,
)
from app.services.traceability_service import TraceabilityService

router = APIRouter()


@router.get("/{project_id}/traceability", response_model=TraceabilityMatrix)
def get_traceability_matrix(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    return TraceabilityService(session).get_matrix(project_id)


@router.get("/{project_id}/traceability/links", response_model=list[TraceabilityLinkResponse])
def list_traceability_links(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    return TraceabilityService(session).list_links(project_id)


@router.post("/{project_id}/traceability/links", response_model=TraceabilityLinkResponse, status_code=201)
def create_traceability_link(
    project_id: uuid.UUID,
    body: TraceabilityLinkCreate,
    session: Session = Depends(get_session),
):
    return TraceabilityService(session).create_link(project_id, body)


@router.delete("/{project_id}/traceability/links/{link_id}", status_code=204)
def delete_traceability_link(
    project_id: uuid.UUID,
    link_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    TraceabilityService(session).delete_link(project_id, link_id)


@router.post("/{project_id}/traceability/auto-link", response_model=AutoLinkResult)
def auto_link(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """Auto-derive traceability links: connects every requirement input to every generated document."""
    return TraceabilityService(session).auto_link(project_id)
