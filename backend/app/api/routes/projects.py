import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.models import User
from app.db.session import get_session
from app.schemas.common import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProjectResponse])
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    session: Session = Depends(get_session),
):
    svc = ProjectService(session)
    return svc.list(page=page, page_size=page_size, status=status)


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate, session: Session = Depends(get_session)):
    svc = ProjectService(session)
    return svc.create(body)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, session: Session = Depends(get_session)):
    svc = ProjectService(session)
    project = svc.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Project {project_id} not found"})
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    session: Session = Depends(get_session),
):
    svc = ProjectService(session)
    project = svc.update(project_id, body)
    if not project:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Project {project_id} not found"})
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error_code": "FORBIDDEN", "message": "Only admins can delete projects"})
    svc = ProjectService(session)
    deleted = svc.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Project {project_id} not found"})
