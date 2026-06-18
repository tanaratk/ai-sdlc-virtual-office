from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="AI-SDLC Working Office",
    version="0.1.0",
    description="Agentic Software Factory — 10-step SDLC pipeline powered by AI agents.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
