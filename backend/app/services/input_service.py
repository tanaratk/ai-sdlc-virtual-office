import uuid

from sqlmodel import Session, func, select

from app.db.models import RequirementInput
from app.schemas.common import PaginatedResponse
from app.schemas.input import RequirementInputCreate, RequirementInputResponse


class InputService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self, project_id: uuid.UUID, page: int, page_size: int
    ) -> PaginatedResponse[RequirementInputResponse]:
        query = select(RequirementInput).where(
            RequirementInput.project_id == project_id
        )
        total = self.session.exec(
            select(func.count()).select_from(query.subquery())
        ).one()
        items = self.session.exec(
            query.offset((page - 1) * page_size).limit(page_size)
        ).all()
        return PaginatedResponse(
            total=total, page=page, page_size=page_size,
            items=[RequirementInputResponse.model_validate(i) for i in items],
        )

    def get(self, project_id: uuid.UUID, input_id: uuid.UUID) -> RequirementInput | None:
        return self.session.exec(
            select(RequirementInput).where(
                RequirementInput.id == input_id,
                RequirementInput.project_id == project_id,
            )
        ).first()

    def create(self, project_id: uuid.UUID, data: RequirementInputCreate) -> RequirementInput:
        item = RequirementInput(project_id=project_id, **data.model_dump())
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, project_id: uuid.UUID, input_id: uuid.UUID) -> bool:
        item = self.get(project_id, input_id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
