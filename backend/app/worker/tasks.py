"""Celery tasks — one per pipeline agent.

Each task accepts run_id as a plain string (UUID) so Celery can JSON-serialize it.
Tasks create their own DB session to be safe across worker processes.
"""
import logging
import uuid

from celery import Task

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# Retry only on transient infrastructure errors, not on business logic failures.
_RETRY_ON = (ConnectionError, OSError, TimeoutError)
_MAX_RETRIES = 2
_RETRY_DELAY = 30  # seconds


class _AgentTask(Task):
    """Base task that logs retries."""

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning("Task %s retrying (attempt %s): %s", task_id, self.request.retries, exc)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("Task %s failed permanently: %s", task_id, exc)


# ── Step 1+2: Requirement → Gap Analysis (auto-chained) ──────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_pipeline_start",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_pipeline_start(self, run_id: str) -> None:
    from app.agents.requirement_agent import RequirementAgentRunner
    from app.agents.gap_analysis_agent import GapAnalysisAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    _id = uuid.UUID(run_id)

    with Session(engine) as session:
        RequirementAgentRunner(session).run(_id)

    with Session(engine) as session:
        GapAnalysisAgentRunner(session).run(_id)


# ── Step 3: BA Agent ──────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_ba_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_ba_agent(self, run_id: str) -> None:
    from app.agents.ba_agent import BAAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        BAAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 4: SA Agent ──────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_sa_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_sa_agent(self, run_id: str) -> None:
    from app.agents.sa_agent import SAAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        SAAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 5: UX Agent ──────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_ux_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_ux_agent(self, run_id: str) -> None:
    from app.agents.ux_agent import UXAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        UXAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 6: Dev Agent ─────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_dev_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_dev_agent(self, run_id: str) -> None:
    from app.agents.dev_agent import DevAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        DevAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 7: DevOps Agent ─────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_devops_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_devops_agent(self, run_id: str) -> None:
    from app.agents.devops_agent import DevOpsAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        DevOpsAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 8: QA Agent ──────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_qa_agent",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_qa_agent(self, run_id: str) -> None:
    from app.agents.qa_agent import QAAgentRunner
    from app.db.session import engine
    from sqlmodel import Session

    with Session(engine) as session:
        QAAgentRunner(session).run(uuid.UUID(run_id))


# ── Dispatch helper ───────────────────────────────────────────────────────────
# Maps step_name → task function.  Used by pipeline.py so it has one place to look.

STEP_TASKS: dict[str, object] = {
    "pipeline_start": run_pipeline_start,
    "ba_documents":   run_ba_agent,
    "sa_documents":   run_sa_agent,
    "ux_documents":   run_ux_agent,
    "dev_tasks":      run_dev_agent,
    "devops_tasks":   run_devops_agent,
    "test_cases":     run_qa_agent,
}
