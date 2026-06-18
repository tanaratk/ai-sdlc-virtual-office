from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Document routes — Sprint 8"})


@router.get("/{project_id}/documents")
def list_documents(project_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/documents/{document_id}")
def get_document(project_id: str, document_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/documents/{document_id}/versions")
def get_document_versions(project_id: str, document_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/documents/{document_id}/approve")
def approve_document(project_id: str, document_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/documents/{document_id}/reject")
def reject_document(project_id: str, document_id: str):
    raise _NOT_IMPL


@router.get("/{project_id}/documents/{document_id}/export")
def export_document(project_id: str, document_id: str):
    raise _NOT_IMPL
