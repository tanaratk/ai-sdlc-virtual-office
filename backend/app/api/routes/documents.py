import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common import PaginatedResponse
from app.schemas.document import DocumentResponse, DocumentSummary
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("/{project_id}/documents", response_model=PaginatedResponse[DocumentSummary])
def list_documents(
    project_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    svc = DocumentService(session)
    return svc.list(project_id, page=page, page_size=page_size)


@router.get("/{project_id}/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = DocumentService(session)
    return svc.get(project_id, document_id)


@router.post("/{project_id}/documents/{document_id}/approve", response_model=DocumentResponse)
def approve_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = DocumentService(session)
    return svc.approve(project_id, document_id)


@router.post("/{project_id}/documents/{document_id}/reject", response_model=DocumentResponse)
def reject_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = DocumentService(session)
    return svc.reject(project_id, document_id)


@router.get("/{project_id}/documents/{document_id}/versions", status_code=501)
def get_document_versions(project_id: uuid.UUID, document_id: uuid.UUID):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Document versions — Sprint 10"})


@router.get("/{project_id}/documents/{document_id}/export", status_code=501)
def export_document(project_id: uuid.UUID, document_id: uuid.UUID):
    raise HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Document export — Sprint 10"})
