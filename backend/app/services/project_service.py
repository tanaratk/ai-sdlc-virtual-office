import uuid
from datetime import UTC, datetime

from sqlmodel import Session, func, select

from app.db.models import Project, ProjectStatus
from app.schemas.common import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self, page: int, page_size: int, status: str | None
    ) -> PaginatedResponse[ProjectResponse]:
        query = select(Project)
        if status:
            query = query.where(Project.status == ProjectStatus(status))

        total = self.session.exec(
            select(func.count()).select_from(query.subquery())
        ).one()
        items = self.session.exec(
            query.offset((page - 1) * page_size).limit(page_size)
        ).all()
        return PaginatedResponse(
            total=total, page=page, page_size=page_size,
            items=[ProjectResponse.model_validate(p) for p in items],
        )

    def get(self, project_id: uuid.UUID) -> Project | None:
        return self.session.get(Project, project_id)

    def create(self, data: ProjectCreate) -> Project:
        project = Project(**data.model_dump())
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def update(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project | None:
        project = self.session.get(Project, project_id)
        if not project:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        project.updated_at = datetime.now(UTC)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: uuid.UUID) -> bool:
        project = self.session.get(Project, project_id)
        if not project:
            return False
        self.session.delete(project)
        self.session.commit()
        return True
