from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_sdlc",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],  # must be explicit — no auto-discover
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
