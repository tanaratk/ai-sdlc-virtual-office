"""Developer Agent — Pipeline Step 6.

Reads the approved FSD, Architecture Design, Database Design, API Spec,
and Screen Specification to produce a Code Task List:
  - Backend implementation tasks
  - Frontend implementation tasks
  - Database migration tasks

IMPORTANT: This agent generates TASK LISTS and SKELETON PLANS only.
It must NOT generate production implementation code.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.models import (
    ActivityLog,
    Agent,
    AgentStatus,
    Document,
    DocumentStatus,
    DocumentType,
    EventType,
    PipelineRun,
    PipelineRunStatus,
    PipelineStep,
    PipelineStepStatus,
)
from app.llm.client import call_ollama, extract_json

logger = logging.getLogger(__name__)

AGENT_NAME = "developer-agent"
STEP_NAME = "dev_tasks"
TIMEOUT_SECONDS = 240.0


# ── Output schema ──────────────────────────────────────────────────────────────

class _Task(BaseModel):
    id: str = "TASK-001"
    category: str = "backend"
    title: str
    description: str
    requirement_refs: list[str] = Field(default_factory=list)
    api_refs: list[str] = Field(default_factory=list)
    db_refs: list[str] = Field(default_factory=list)
    screen_refs: list[str] = Field(default_factory=list)
    priority: str = "High"
    estimated_hours: int = 4


class _MigrationTask(BaseModel):
    id: str = "MIG-001"
    table: str
    operation: str = "create_table"
    description: str
    db_ref: str = ""


class DevAgentOutput(BaseModel):
    backend_tasks: list[_Task] = Field(default_factory=list)
    frontend_tasks: list[_Task] = Field(default_factory=list)
    database_migrations: list[_MigrationTask] = Field(default_factory=list)
    total_estimated_hours: int = 0
    notes: list[str] = Field(default_factory=list)


# ── Prompts ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are the Developer Agent in an AI-powered software factory.
Your job is to read the approved FSD, Architecture Design, Database Design,
API Specification, and Screen Specification, then produce a structured
Code Task List for the development team.

CRITICAL RULES:
- Generate TASK LISTS and SKELETON PLANS ONLY. Do NOT write implementation code.
- Every task must reference at least one requirement ID (FR-XXX).
- Backend tasks must reference an API endpoint ID (API-XXX) where applicable.
- Frontend tasks must reference a screen ID (UI-XXX) where applicable.
- Database migration tasks must reference a table ID (DB-XXX).
- Task IDs must be sequential: TASK-001, TASK-002, … (backend and frontend share same sequence).
- Migration IDs must be sequential: MIG-001, MIG-002, …
- Estimate hours honestly per task (1–16 hours).
- You MUST return ONLY a valid JSON object — no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following approved technical documents and produce a
Code Task List for backend, frontend, and database migration.
Return ONLY the JSON — no explanation, no code fences.

Schema:
{{
  "backend_tasks": [
    {{
      "id": "TASK-001",
      "category": "backend",
      "title": "short task title",
      "description": "what needs to be implemented — no code, just description",
      "requirement_refs": ["FR-001"],
      "api_refs": ["API-001"],
      "db_refs": ["DB-001"],
      "screen_refs": [],
      "priority": "High|Medium|Low",
      "estimated_hours": 4
    }}
  ],
  "frontend_tasks": [
    {{
      "id": "TASK-010",
      "category": "frontend",
      "title": "short task title",
      "description": "what UI component or page needs to be built",
      "requirement_refs": ["FR-001"],
      "api_refs": ["API-001"],
      "db_refs": [],
      "screen_refs": ["UI-001"],
      "priority": "High|Medium|Low",
      "estimated_hours": 4
    }}
  ],
  "database_migrations": [
    {{
      "id": "MIG-001",
      "table": "table_name",
      "operation": "create_table|add_column|add_index|create_enum",
      "description": "what this migration does",
      "db_ref": "DB-001"
    }}
  ],
  "total_estimated_hours": 40,
  "notes": ["important implementation note or dependency"]
}}

FUNCTIONAL SPECIFICATION DOCUMENT (FSD):
{fsd}

ARCHITECTURE DESIGN:
{architecture}

DATABASE DESIGN:
{database}

API SPECIFICATION:
{api_spec}

SCREEN SPECIFICATION:
{screen_spec}
"""


# ── Markdown renderer ──────────────────────────────────────────────────────────

def _render_task_list(data: DevAgentOutput, project_id: str, doc_id: str) -> str:
    def _task_rows(tasks: list[_Task]) -> str:
        if not tasks:
            return "> No tasks defined."
        rows = ""
        for t in tasks:
            refs = ", ".join(t.requirement_refs) if t.requirement_refs else "—"
            api = ", ".join(t.api_refs) if t.api_refs else "—"
            db = ", ".join(t.db_refs) if t.db_refs else "—"
            ui = ", ".join(t.screen_refs) if t.screen_refs else "—"
            rows += f"""
#### {t.id} [{t.priority}] — {t.title}

{t.description}

| Requirement Refs | API Refs | DB Refs | Screen Refs | Est. Hours |
|---|---|---|---|---|
| {refs} | {api} | {db} | {ui} | {t.estimated_hours}h |

"""
        return rows

    def _migration_rows(migrations: list[_MigrationTask]) -> str:
        if not migrations:
            return "| — | — | — | — |\n"
        rows = ""
        for m in migrations:
            rows += f"| {m.id} | `{m.table}` | {m.operation} | {m.description} |\n"
        return rows

    backend_total = sum(t.estimated_hours for t in data.backend_tasks)
    frontend_total = sum(t.estimated_hours for t in data.frontend_tasks)

    notes_section = "\n".join(f"- {n}" for n in data.notes) \
        if data.notes else "> No additional notes."

    return f"""\
# Code Task List

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Developer Agent v1.0.0
**Pipeline Step:** 6 of 10
**Status:** Draft → Awaiting Review

> ⚠️ This document contains TASK LISTS only. No implementation code is generated
> until all upstream documents are approved and this task list is reviewed.

---

## Summary

| Category | Tasks | Estimated Hours |
|---|---|---|
| Backend | {len(data.backend_tasks)} | {backend_total}h |
| Frontend | {len(data.frontend_tasks)} | {frontend_total}h |
| DB Migrations | {len(data.database_migrations)} | — |
| **Total** | **{len(data.backend_tasks) + len(data.frontend_tasks)}** | **{data.total_estimated_hours}h** |

---

## 1. Backend Tasks

{_task_rows(data.backend_tasks)}

---

## 2. Frontend Tasks

{_task_rows(data.frontend_tasks)}

---

## 3. Database Migrations

| ID | Table | Operation | Description |
|---|---|---|---|
{_migration_rows(data.database_migrations)}

---

## 4. Implementation Notes

{notes_section}
"""


# ── Agent runner ───────────────────────────────────────────────────────────────

class DevAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("DevAgent skipped — run %s already failed", run_id)
                return

            step = self._get_step(run_id)
            agent_row = self._get_agent_row()

            run.status = PipelineRunStatus.running
            run.current_step = STEP_NAME
            step.status = PipelineStepStatus.running
            step.started_at = datetime.utcnow()
            if agent_row:
                agent_row.status = AgentStatus.working
                agent_row.updated_at = datetime.utcnow()
            self.session.commit()

            fsd_doc, arch_doc, db_doc, api_doc, screen_doc = \
                self._load_source_documents(run.project_id)

            raw_json = call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    fsd=fsd_doc.content_markdown,
                    architecture=arch_doc.content_markdown,
                    database=db_doc.content_markdown,
                    api_spec=api_doc.content_markdown,
                    screen_spec=screen_doc.content_markdown,
                ),
                timeout=TIMEOUT_SECONDS,
            )

            parsed = extract_json(raw_json)
            output = DevAgentOutput.model_validate(parsed)

            task_doc_id = uuid.uuid4()
            pid = str(run.project_id)

            task_doc = Document(
                id=task_doc_id,
                project_id=run.project_id,
                document_type=DocumentType.code_task_list,
                title="Code Task List",
                content_markdown=_render_task_list(output, pid, str(task_doc_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(task_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = task_doc.id
            step.completed_at = datetime.utcnow()

            # Gate 5 — wait for human review before any code is written
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.utcnow()

            backend_h = sum(t.estimated_hours for t in output.backend_tasks)
            frontend_h = sum(t.estimated_hours for t in output.frontend_tasks)
            self._log_activity(
                run.project_id, agent_row,
                f"Code task list created: {len(output.backend_tasks)} backend tasks ({backend_h}h), "
                f"{len(output.frontend_tasks)} frontend tasks ({frontend_h}h), "
                f"{len(output.database_migrations)} migrations. Awaiting Gate 5 review.",
            )
            self.session.commit()
            logger.info(
                "DevAgent completed run=%s doc=%s be_tasks=%d fe_tasks=%d migs=%d",
                run_id, task_doc_id,
                len(output.backend_tasks), len(output.frontend_tasks),
                len(output.database_migrations),
            )

        except Exception as exc:
            logger.exception("DevAgent failed run=%s: %s", run_id, exc)
            self.session.rollback()

            try:
                run = self.session.get(PipelineRun, run_id)
                if run:
                    run.status = PipelineRunStatus.failed
                if step:
                    step.status = PipelineStepStatus.failed
                    step.error_message = str(exc)[:2000]
                if agent_row:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.utcnow()
                self.session.commit()
            except Exception:
                logger.exception("Failed to persist failure state for run=%s", run_id)

    # ── helpers ────────────────────────────────────────────────────────────────

    def _get_run(self, run_id: uuid.UUID) -> PipelineRun:
        run = self.session.get(PipelineRun, run_id)
        if not run:
            raise ValueError(f"PipelineRun {run_id} not found")
        return run

    def _get_step(self, run_id: uuid.UUID) -> PipelineStep:
        step = self.session.exec(
            select(PipelineStep).where(
                PipelineStep.pipeline_run_id == run_id,
                PipelineStep.step_name == STEP_NAME,
            )
        ).first()
        if not step:
            raise ValueError(f"PipelineStep {STEP_NAME} not found for run {run_id}")
        return step

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_source_documents(
        self, project_id: uuid.UUID
    ) -> tuple[Document, Document, Document, Document, Document]:
        def _latest(doc_type: DocumentType) -> Optional[Document]:
            return self.session.exec(
                select(Document).where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                ).order_by(Document.created_at.desc())
            ).first()

        fsd = _latest(DocumentType.fsd)
        arch = _latest(DocumentType.architecture_design)
        db = _latest(DocumentType.database_design)
        api = _latest(DocumentType.api_spec)
        screen = _latest(DocumentType.screen_spec)

        missing = [
            name for name, doc in [
                ("FSD", fsd), ("Architecture", arch), ("Database", db),
                ("API Spec", api), ("Screen Spec", screen),
            ] if not doc
        ]
        if missing:
            raise ValueError(f"Missing source documents: {', '.join(missing)}")

        return fsd, arch, db, api, screen  # type: ignore[return-value]

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
