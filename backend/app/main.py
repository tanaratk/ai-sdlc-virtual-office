import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes import ws as ws_routes
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def _recover_stuck_runs() -> None:
    """Mark pipeline runs left in status=running as failed on server restart.

    Without this, the DB stays 'running' forever when the Celery worker
    or backend restarts mid-task.
    """
    try:
        from app.db.models import PipelineRun, PipelineRunStatus
        from app.db.session import engine
        from sqlmodel import Session, select

        with Session(engine) as session:
            stuck = session.exec(
                select(PipelineRun).where(
                    PipelineRun.status == PipelineRunStatus.running
                )
            ).all()
            if stuck:
                for run in stuck:
                    run.status = PipelineRunStatus.failed
                session.commit()
                logger.warning(
                    "Startup recovery: marked %d stuck pipeline run(s) as failed. "
                    "Use the Retry button to re-run.",
                    len(stuck),
                )
    except Exception:
        # Never block startup — DB may not be ready on first boot.
        logger.exception("Startup recovery failed (non-fatal)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _recover_stuck_runs()
    yield


app = FastAPI(
    title="AI-SDLC Working Office",
    version="0.1.0",
    description="Agentic Software Factory — 10-step SDLC pipeline powered by AI agents.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

_origins = (
    ["*"] if settings.app_debug
    else [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_routes.router)  # WebSocket at /ws/office (no api/v1 prefix)
