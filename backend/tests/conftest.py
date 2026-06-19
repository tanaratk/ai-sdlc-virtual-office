import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import patch

from app.db.session import get_session
from app.main import app


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(_engine)
    return _engine


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, engine):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with patch("app.api.routes.pipeline.engine", engine):
        with TestClient(app) as client:
            yield client

    app.dependency_overrides.clear()
