"""Celery tasks — one per pipeline agent.

Each task accepts run_id as a plain string (UUID) so Celery can JSON-serialize it.
Tasks create their own DB session to be safe across worker processes.
"""
import logging
import uuid
from datetime import UTC, datetime

from celery import Task
from sqlmodel import Session, select

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


# ── Step 6: Technical Design Agent ───────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_technical_design",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_technical_design(self, run_id: str) -> None:
    from app.agents.technical_design_agent import TechnicalDesignAgentRunner
    from app.db.session import engine

    with Session(engine) as session:
        TechnicalDesignAgentRunner(session).run(uuid.UUID(run_id))


# ── Step 7: Code Review Agent ─────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_code_review",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_code_review(self, run_id: str) -> None:
    from app.agents.code_review_agent import CodeReviewAgentRunner
    from app.db.session import engine

    with Session(engine) as session:
        CodeReviewAgentRunner(session).run(uuid.UUID(run_id))


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


# ── Pipeline step helper ──────────────────────────────────────────────────────

def _step_init(session: Session, run_id: uuid.UUID, step_name: str):
    """Set run + step to running state. Returns (run, step) or (None, None)."""
    from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus

    run = session.get(PipelineRun, run_id)
    if not run or run.status == PipelineRunStatus.failed:
        return None, None

    step = session.exec(
        select(PipelineStep).where(
            PipelineStep.pipeline_run_id == run_id,
            PipelineStep.step_name == step_name,
        )
    ).first()
    if not step:
        logger.error("No %s step found for run %s", step_name, run_id)
        return None, None

    run.status = PipelineRunStatus.running
    run.current_step = step_name
    step.status = PipelineStepStatus.running
    step.started_at = datetime.now(UTC)
    session.commit()
    return run, step


def _step_complete(session: Session, run_id: uuid.UUID, step_name: str, doc_id: uuid.UUID) -> None:
    """Mark step completed, set run to waiting_for_user."""
    from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus

    run = session.get(PipelineRun, run_id)
    step = session.exec(
        select(PipelineStep).where(
            PipelineStep.pipeline_run_id == run_id,
            PipelineStep.step_name == step_name,
        )
    ).first()
    if step:
        step.status = PipelineStepStatus.completed
        step.output_document_id = doc_id
        step.completed_at = datetime.now(UTC)
    if run:
        run.status = PipelineRunStatus.waiting_for_user
        run.current_step = step_name
    session.commit()


def _step_fail(session: Session, run_id: uuid.UUID, step_name: str, error: str) -> None:
    """Mark step + run as failed."""
    from app.db.models import PipelineRun, PipelineRunStatus, PipelineStep, PipelineStepStatus

    try:
        run = session.get(PipelineRun, run_id)
        step = session.exec(
            select(PipelineStep).where(
                PipelineStep.pipeline_run_id == run_id,
                PipelineStep.step_name == step_name,
            )
        ).first()
        if run:
            run.status = PipelineRunStatus.failed
        if step:
            step.status = PipelineStepStatus.failed
            step.error_message = error[:2000]
        session.commit()
    except Exception:
        logger.exception("Failed to persist failure state run=%s step=%s", run_id, step_name)


# ── Step 8: Change Impact Agent (pipeline baseline) ──────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_change_impact_pipeline",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_change_impact_pipeline(self, run_id: str) -> None:
    from app.agents.change_impact_agent import ChangeImpactAgentRunner
    from app.db.session import engine

    STEP = "change_impact"
    _id = uuid.UUID(run_id)

    with Session(engine) as session:
        run, step = _step_init(session, _id, STEP)
        if not run:
            return
        try:
            doc = ChangeImpactAgentRunner(session).run(
                project_id=run.project_id,
                change_description=(
                    "Pipeline Step 8 — automated baseline impact assessment of all project requirements."
                ),
                changed_requirement_ids=[],
                context_notes="Generated automatically during SDLC pipeline execution.",
            )
            _step_complete(session, _id, STEP, doc.id)
        except Exception as exc:
            logger.exception("Change Impact pipeline task failed run=%s: %s", _id, exc)
            session.rollback()
            _step_fail(session, _id, STEP, str(exc))


# ── Step 9: Documentation Agent ───────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_documentation_pipeline",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_documentation_pipeline(self, run_id: str) -> None:
    from app.agents.documentation_agent import DocumentationAgentRunner
    from app.db.models import PipelineRun, Project
    from app.db.session import engine

    STEP = "documentation"
    _id = uuid.UUID(run_id)

    with Session(engine) as session:
        run, step = _step_init(session, _id, STEP)
        if not run:
            return
        project = session.get(Project, run.project_id)
        project_name = project.name if project else "Project"
        try:
            doc = DocumentationAgentRunner(session).run(
                project_id=run.project_id,
                project_name=project_name,
            )
            _step_complete(session, _id, STEP, doc.id)
        except Exception as exc:
            logger.exception("Documentation pipeline task failed run=%s: %s", _id, exc)
            session.rollback()
            _step_fail(session, _id, STEP, str(exc))


# ── Step 10: PM Agent ─────────────────────────────────────────────────────────

@celery_app.task(
    base=_AgentTask,
    bind=True,
    name="tasks.run_pm_pipeline",
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_DELAY,
    autoretry_for=_RETRY_ON,
)
def run_pm_pipeline(self, run_id: str) -> None:
    from app.agents.pm_agent import PMAgentRunner
    from app.db.models import PipelineRun, Project
    from app.db.session import engine

    STEP = "pm_summary"
    _id = uuid.UUID(run_id)

    with Session(engine) as session:
        run, step = _step_init(session, _id, STEP)
        if not run:
            return
        project = session.get(Project, run.project_id)
        project_name = project.name if project else "Project"
        try:
            project_summary_doc, _delivery_doc = PMAgentRunner(session).run(
                project_id=run.project_id,
                project_name=project_name,
            )
            _step_complete(session, _id, STEP, project_summary_doc.id)
        except Exception as exc:
            logger.exception("PM pipeline task failed run=%s: %s", _id, exc)
            session.rollback()
            _step_fail(session, _id, STEP, str(exc))


# ── Dispatch helper ───────────────────────────────────────────────────────────
# Maps step_name → task function.  Used by pipeline.py so it has one place to look.

STEP_TASKS: dict[str, object] = {
    # Business Layer
    "pipeline_start":    run_pipeline_start,
    "ba_documents":      run_ba_agent,
    # Design Layer
    "sa_documents":      run_sa_agent,
    "ux_documents":      run_ux_agent,
    "technical_design":  run_technical_design,
    # Delivery Layer
    "dev_tasks":         run_dev_agent,
    "code_review":       run_code_review,
    "devops_tasks":      run_devops_agent,
    "test_cases":        run_qa_agent,
    # On-demand (not in auto-chain)
    "change_impact":     run_change_impact_pipeline,
    "documentation":     run_documentation_pipeline,
    "pm_summary":        run_pm_pipeline,
}
