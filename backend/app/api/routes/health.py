from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from app.db.session import get_session

router = APIRouter()


@router.get("/health")
def health_check(session: Session = Depends(get_session)) -> dict:
    try:
        session.exec(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status}
