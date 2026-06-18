import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common import PaginatedResponse
from app.schemas.input import RequirementInputCreate, RequirementInputResponse
from app.services.input_service import InputService

router = APIRouter()


@router.get("/{project_id}/inputs", response_model=PaginatedResponse[RequirementInputResponse])
def list_inputs(
    project_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    svc = InputService(session)
    return svc.list(project_id=project_id, page=page, page_size=page_size)


@router.post("/{project_id}/inputs", response_model=RequirementInputResponse, status_code=201)
def create_input(
    project_id: uuid.UUID,
    body: RequirementInputCreate,
    session: Session = Depends(get_session),
):
    svc = InputService(session)
    return svc.create(project_id=project_id, data=body)


@router.get("/{project_id}/inputs/{input_id}", response_model=RequirementInputResponse)
def get_input(
    project_id: uuid.UUID,
    input_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = InputService(session)
    item = svc.get(project_id=project_id, input_id=input_id)
    if not item:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Input {input_id} not found"})
    return item


@router.delete("/{project_id}/inputs/{input_id}", status_code=204)
def delete_input(
    project_id: uuid.UUID,
    input_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    svc = InputService(session)
    deleted = svc.delete(project_id=project_id, input_id=input_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Input {input_id} not found"})
