import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from app.db.models import ActivityLog
from app.db.session import get_session
from app.schemas.activity import ActivityLogList, ActivityLogResponse

router = APIRouter()


@router.get("/{project_id}/activity", response_model=ActivityLogList)
def get_activity(
    project_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(ActivityLog).where(ActivityLog.project_id == project_id)
    if event_type:
        query = query.where(ActivityLog.event_type == event_type)
    query = query.order_by(ActivityLog.created_at.desc())

    total = session.exec(
        select(func.count()).select_from(query.subquery())
    ).one()
    items = session.exec(query.offset(offset).limit(limit)).all()

    return ActivityLogList(
        total=total,
        items=[ActivityLogResponse.model_validate(a) for a in items],
    )
