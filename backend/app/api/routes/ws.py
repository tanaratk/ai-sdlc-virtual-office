"""WebSocket endpoint for Virtual Office real-time agent status.

Clients connect to /ws/office and receive agent status pushes every ~1 second.
This works with the Celery-based pipeline: Celery tasks update the DB, and this
handler reads DB changes and broadcasts them to all connected clients.
"""
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

from app.db.models import Agent
from app.db.session import engine

logger = logging.getLogger(__name__)
router = APIRouter()

POLL_INTERVAL = 1.0  # seconds between DB reads


def _read_agent_statuses() -> dict[str, dict]:
    """Sync DB read — called via asyncio.to_thread to avoid blocking event loop."""
    with Session(engine) as session:
        agents = session.exec(select(Agent).where(Agent.is_active == True)).all()  # noqa: E712
        return {
            a.role: {
                "status":   a.status.value,
                "model":    a.model_name,
                "provider": a.model_provider.value,
            }
            for a in agents
        }


@router.websocket("/ws/office")
async def office_websocket(websocket: WebSocket) -> None:
    """Push agent status changes to the Virtual Office in real-time."""
    await websocket.accept()
    logger.info("Virtual Office WebSocket connected from %s", websocket.client)
    last_statuses: dict[str, str] = {}

    try:
        while True:
            statuses = await asyncio.to_thread(_read_agent_statuses)
            if statuses != last_statuses:
                await websocket.send_json({"type": "agent_statuses", "data": statuses})
                last_statuses = statuses
            await asyncio.sleep(POLL_INTERVAL)
    except WebSocketDisconnect:
        logger.info("Virtual Office WebSocket disconnected")
    except Exception:
        logger.exception("Virtual Office WebSocket error")
