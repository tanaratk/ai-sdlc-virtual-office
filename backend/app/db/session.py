from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
    **({} if _is_sqlite else {"pool_size": 10, "max_overflow": 20}),
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
