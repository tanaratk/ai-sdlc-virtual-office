"""WebSocket endpoint for Virtual Office real-time agent status + pipeline events.

Two message types are emitted:
  {"type": "agent_statuses",  "data": {role: {status, model, provider, current_task}}}
  {"type": "pipeline_event",  "event": "step_running|step_completed|step_failed",
   "step_name": "...", "project_name": "...", "project_id": "...", "timestamp": "..."}
"""
import asyncio
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

from app.db.models import (
    Agent,
    PipelineRun,
    PipelineRunStatus,
    PipelineStep,
    PipelineStepStatus,
    Project,
)
from app.db.session import engine

logger = logging.getLogger(__name__)
router = APIRouter()

POLL_INTERVAL = 1.0  # seconds between DB reads


# ── DB reads (sync, called via asyncio.to_thread) ─────────────────────────────

def _read_agent_statuses() -> dict[str, dict]:
    """Agent status + current running step name, keyed by role."""
    with Session(engine) as session:
        agents = session.exec(select(Agent).where(Agent.is_active == True)).all()  # noqa: E712

        # Map agent_id → step_name for currently running steps
        running_steps = session.exec(
            select(PipelineStep).where(PipelineStep.status == PipelineStepStatus.running)
        ).all()
        agent_task: dict[str, str] = {
            str(s.agent_id): s.step_name for s in running_steps if s.agent_id
        }

        return {
            a.role: {
                "status":       a.status.value,
                "model":        a.model_name,
                "provider":     a.model_provider.value,
                "current_task": agent_task.get(str(a.id), ""),
            }
            for a in agents
        }


def _read_pipeline_steps() -> list[dict]:
    """All steps from active runs (running or pending), with project name."""
    with Session(engine) as session:
        active_runs = session.exec(
            select(PipelineRun).where(
                PipelineRun.status.in_([  # type: ignore[union-attr]
                    PipelineRunStatus.running,
                    PipelineRunStatus.pending,
                ])
            )
        ).all()

        if not active_runs:
            return []

        # Gather project names
        project_ids = list({r.project_id for r in active_runs})
        projects = session.exec(
            select(Project).where(Project.id.in_(project_ids))  # type: ignore[arg-type]
        ).all()
        project_name_map: dict[uuid.UUID, str] = {p.id: p.name for p in projects}
        run_project_map: dict[uuid.UUID, uuid.UUID] = {r.id: r.project_id for r in active_runs}

        steps: list[dict] = []
        for run in active_runs:
            run_steps = session.exec(
                select(PipelineStep).where(PipelineStep.pipeline_run_id == run.id)
            ).all()
            proj_id = run_project_map[run.id]
            proj_name = project_name_map.get(proj_id, "Unknown")
            for s in run_steps:
                steps.append({
                    "id":           str(s.id),
                    "step_name":    s.step_name,
                    "status":       s.status.value,
                    "project_name": proj_name,
                    "project_id":   str(proj_id),
                })

        return steps


# ── WebSocket endpoint ─────────────────────────────────────────────────────────

@router.websocket("/ws/office")
async def office_websocket(websocket: WebSocket) -> None:
    """Push agent statuses and pipeline events to the Virtual Office."""
    await websocket.accept()
    logger.info("Virtual Office WebSocket connected from %s", websocket.client)

    last_agent_data: dict = {}
    last_step_statuses: dict[str, str] = {}  # step_id → status

    try:
        while True:
            # ── Agent statuses ──────────────────────────────────────────────
            agent_data = await asyncio.to_thread(_read_agent_statuses)
            if agent_data != last_agent_data:
                await websocket.send_json({"type": "agent_statuses", "data": agent_data})
                last_agent_data = agent_data

            # ── Pipeline events (detect step status changes) ─────────────
            steps = await asyncio.to_thread(_read_pipeline_steps)
            for step in steps:
                step_id   = step["id"]
                new_status = step["status"]
                old_status = last_step_statuses.get(step_id)

                last_step_statuses[step_id] = new_status

                # Only emit when status actually changes (not on first sight)
                if old_status is not None and old_status != new_status:
                    event_name = {
                        "running":   "step_running",
                        "completed": "step_completed",
                        "failed":    "step_failed",
                        "skipped":   "step_skipped",
                    }.get(new_status)
                    if event_name:
                        await websocket.send_json({
                            "type":         "pipeline_event",
                            "event":        event_name,
                            "step_name":    step["step_name"],
                            "project_name": step["project_name"],
                            "project_id":   step["project_id"],
                            "timestamp":    datetime.now(UTC).isoformat(),
                        })

            await asyncio.sleep(POLL_INTERVAL)

    except WebSocketDisconnect:
        logger.info("Virtual Office WebSocket disconnected")
    except Exception:
        logger.exception("Virtual Office WebSocket error")
