"""Technical Design Agent -- Pipeline Step 6 (Design Layer).

Reads the approved FSD, Architecture, DB Schema, API Spec, and Screen Spec
and produces a detailed dev_tasks.md:
  - TASK-XXX items with domain, file_path, FR reference, dependencies
  - Developer Agent instance count recommendation (1 / 2 / 3)

This is the hard gate before the Delivery Layer starts.
"""
import logging
import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator
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
    Project,
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "technical-design-agent"
STEP_NAME = "technical_design"
TIMEOUT_SECONDS = 300.0


# -- Output schema -------------------------------------------------------------

def _first(data: dict, *keys: str, fallback: str = "") -> str:
    for k in keys:
        if k in data and data[k]:
            return str(data[k])
    return fallback


class _Task(BaseModel):
    id: str = "TASK-001"
    domain: str = "backend"
    file_path: str = ""
    description: str = ""
    fr_refs: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    estimated_lines: int = 50

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if not isinstance(v, dict):
            return v
        if not v.get("id"):
            v["id"] = "TASK-001"
        if not v.get("domain"):
            v["domain"] = "backend"
        if not v.get("file_path"):
            v["file_path"] = "src/main"
        if not v.get("description"):
            v["description"] = "Implementation task"
        # normalise fr_refs / fr_ref
        if not v.get("fr_refs"):
            v["fr_refs"] = [v.get("fr_ref", "FR-001")]
        # normalise estimated_lines
        try:
            v["estimated_lines"] = int(v.get("estimated_lines", 50))
        except (TypeError, ValueError):
            v["estimated_lines"] = 50
        return v


class TechnicalDesignOutput(BaseModel):
    tasks: list[_Task] = Field(default_factory=list)
    summary: str = ""
    developer_instances: int = 1

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if not isinstance(v, dict):
            return v
        count = len(v.get("tasks", []))
        if count <= 30:
            v["developer_instances"] = 1
        elif count <= 80:
            v["developer_instances"] = 2
        else:
            v["developer_instances"] = 3
        if not v.get("summary"):
            v["summary"] = f"{count} implementation tasks generated."
        return v


# -- Prompts -------------------------------------------------------------------

def _tech_stack_prompt_vars(tech_stack: dict | None) -> tuple[str, str, str]:
    """Return (tech_stack_info, file_path_examples, file_ext_example) for prompts."""
    if not tech_stack:
        return (
            "FastAPI + SQLModel + PostgreSQL for backend; React + TypeScript + Vite + Tailwind for frontend.",
            '"app/backend/api/routes/users.py" or "app/frontend/src/pages/LoginPage.tsx"',
            "relative/path/to/file.py",
        )
    backend = (tech_stack.get("backend") or "").lower()
    frontend = (tech_stack.get("frontend") or "").lower()
    parts = []
    for key, label in [
        ("backend", "Backend"), ("backend_version", "Backend version"),
        ("frontend", "Frontend"), ("frontend_version", "Frontend version"),
        ("database", "Database"), ("language", "Language"),
        ("orm", "ORM"), ("auth", "Auth"), ("testing", "Testing framework"),
        ("api_docs", "API docs"), ("cloud", "Cloud"),
    ]:
        if tech_stack.get(key):
            parts.append(f"{label}: {tech_stack[key]}")
    info = "; ".join(parts) + "."

    is_dotnet = any(k in backend or k in frontend for k in [".net", "asp.net", "aspnet", "blazor", "razor", "c#"])
    is_node   = any(k in backend for k in ["node", "express", "nest"])
    is_angular = "angular" in frontend
    is_vue     = "vue" in frontend

    if is_dotnet:
        examples = '"Controllers/UsersController.cs" or "Pages/Login.aspx" or "Models/User.cs" or "Views/Users/Index.cshtml"'
        ext_ex   = "Controllers/ItemsController.cs"
    elif is_angular:
        examples = '"frontend/src/app/components/users/users.component.ts" or "backend/src/routes/users.ts" or "backend/src/models/user.ts"'
        ext_ex   = "frontend/src/app/pages/items/items.component.ts"
    elif is_vue:
        examples = '"frontend/src/pages/UsersPage.vue" or "frontend/src/components/UserCard.vue" or "backend/src/routes/users.ts"'
        ext_ex   = "frontend/src/pages/ItemsPage.vue"
    elif is_node:
        examples = '"backend/src/routes/users.ts" or "backend/src/models/user.ts" or "frontend/src/pages/LoginPage.tsx"'
        ext_ex   = "backend/src/routes/items.ts"
    else:
        examples = '"app/backend/api/routes/users.py" or "app/frontend/src/pages/LoginPage.tsx"'
        ext_ex   = "app/backend/api/routes/items.py"

    return info, examples, ext_ex


# -- Prompts -------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are the Technical Design Agent in an AI-powered software factory.
Your job is to read the FSD, Architecture, Database Design, API Spec, and Screen Spec
and produce a comprehensive implementation task breakdown (dev_tasks.md).

PROJECT TECH STACK: {tech_stack_info}

Rules:
- Every task must have a unique ID: TASK-001, TASK-002, ...
- domain must be one of: backend, frontend, database, test, infra
- file_path is the relative path of the file that will be created or modified
  Use file extensions that match the PROJECT TECH STACK above.
  (e.g. {file_path_examples})
- fr_refs must list at least one FR-XXX reference
- depends_on lists TASK-IDs that must complete first (empty list if no dependency)
- estimated_lines is an integer estimate of lines of code for this task
- Cover ALL components from Architecture, ALL tables from DB Design,
  ALL endpoints from API Spec, ALL screens from Screen Spec
- You MUST return ONLY a valid JSON object -- no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following design documents and produce a complete implementation task list.
Return ONLY the JSON -- no explanation, no code fences.

Schema:
{{
  "tasks": [
    {{
      "id": "TASK-001",
      "domain": "backend|frontend|database|test|infra",
      "file_path": "{file_ext_example}",
      "description": "What this task implements",
      "fr_refs": ["FR-001"],
      "depends_on": ["TASK-XXX"],
      "estimated_lines": 80
    }}
  ],
  "summary": "N tasks total: X backend, Y frontend, Z database, ..."
}}

--- FSD ---
{fsd}

--- Architecture ---
{architecture}

--- Database Design ---
{db_schema}

--- API Specification ---
{api_spec}

--- Screen Specification ---
{screen_spec}
"""


# -- Renderers -----------------------------------------------------------------

def _render_technical_design(output: TechnicalDesignOutput, project_id: str, doc_id: str) -> str:
    domain_counts: dict[str, int] = {}
    for t in output.tasks:
        domain_counts[t.domain] = domain_counts.get(t.domain, 0) + 1

    domain_summary = " | ".join(f"{d}: {c}" for d, c in sorted(domain_counts.items()))

    rows = "\n".join(
        f"| {t.id} | {t.domain} | `{t.file_path}` | {t.description[:60]} | "
        f"{', '.join(t.fr_refs)} | {', '.join(t.depends_on) or '-'} | {t.estimated_lines} |"
        for t in output.tasks
    )

    detail_blocks = ""
    for t in output.tasks:
        deps = ", ".join(t.depends_on) if t.depends_on else "None"
        refs = ", ".join(t.fr_refs)
        detail_blocks += f"""
### {t.id} — {t.description}

| Field | Value |
|-------|-------|
| Domain | `{t.domain}` |
| File | `{t.file_path}` |
| FR refs | {refs} |
| Depends on | {deps} |
| Est. lines | {t.estimated_lines} |

"""

    return f"""\
# Technical Design — Task Breakdown

> **Document ID:** TD-{doc_id[:8]}
> **Project:** {project_id[:8]}
> **Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}

## Summary

{output.summary}

**Domain breakdown:** {domain_summary}
**Total tasks:** {len(output.tasks)}
**Recommended Developer Agent instances:** {output.developer_instances}

> Developer Agent scaling:
> - 1 instance: ≤ 30 tasks
> - 2 instances: 31 – 80 tasks
> - 3 instances: > 80 tasks

## Task Table

| ID | Domain | File | Description | FR refs | Depends on | Est. lines |
|----|--------|------|-------------|---------|------------|-----------|
{rows}

## Task Details
{detail_blocks}
"""


# -- Runner --------------------------------------------------------------------

class TechnicalDesignAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("TechnicalDesignAgent skipped -- run %s already failed", run_id)
                return

            step = self._get_step(run_id)
            agent_row = self._get_agent_row()

            run.status = PipelineRunStatus.running
            run.current_step = STEP_NAME
            step.status = PipelineStepStatus.running
            step.started_at = datetime.now(UTC)
            if agent_row:
                agent_row.status = AgentStatus.working
                agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

            fsd_doc, arch_doc, db_doc, api_doc, screen_doc = self._load_design_documents(run.project_id)

            project = self.session.get(Project, run.project_id)
            tech_stack: dict | None = project.tech_stack if project else None
            tech_stack_info, file_path_examples, file_ext_example = _tech_stack_prompt_vars(tech_stack)

            _DOC_LIMIT = 1500  # chars per doc — 5 docs x 1500 = 7500 chars input
            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT.format(
                    tech_stack_info=tech_stack_info,
                    file_path_examples=file_path_examples,
                ),
                user_prompt=_TASK_TEMPLATE.format(
                    file_ext_example=file_ext_example,
                    fsd=fsd_doc.content_markdown[:_DOC_LIMIT],
                    architecture=arch_doc.content_markdown[:_DOC_LIMIT],
                    db_schema=db_doc.content_markdown[:_DOC_LIMIT],
                    api_spec=api_doc.content_markdown[:_DOC_LIMIT],
                    screen_spec=screen_doc.content_markdown[:_DOC_LIMIT],
                ),
                model=agent_row.model_name if agent_row else None,
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = TechnicalDesignOutput.model_validate(parsed)

            doc_id = uuid.uuid4()
            pid = str(run.project_id)
            markdown = _render_technical_design(output, pid, str(doc_id))

            doc = Document(
                id=doc_id,
                project_id=run.project_id,
                document_type=DocumentType.technical_design,
                title=f"Technical Design — {len(output.tasks)} Tasks ({output.developer_instances} Dev instance{'s' if output.developer_instances > 1 else ''})",
                content_markdown=markdown,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = doc.id
            step.completed_at = datetime.now(UTC)

            # Design Layer gate -- wait for human review before Delivery Layer
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            self._log_activity(
                run.project_id, agent_row,
                f"Technical Design complete: {len(output.tasks)} tasks "
                f"({output.developer_instances} Developer Agent instance(s)). "
                f"Awaiting Design Layer gate review.",
            )
            self.session.commit()

            from app.agents._workspace import write_workspace_docs
            write_workspace_docs(self.session, run.project_id, {"dev_tasks.md": markdown})
            logger.info("TechnicalDesignAgent completed run=%s doc=%s tasks=%d", run_id, doc_id, len(output.tasks))

        except Exception as exc:
            logger.exception("TechnicalDesignAgent failed run=%s: %s", run_id, exc)
            self.session.rollback()
            if step:
                step.status = PipelineStepStatus.failed
                step.error_message = str(exc)
                step.completed_at = datetime.now(UTC)
            if agent_row:
                agent_row.status = AgentStatus.error
                agent_row.updated_at = datetime.now(UTC)
            run2 = self.session.get(PipelineRun, run_id)
            if run2:
                run2.status = PipelineRunStatus.failed
            self.session.commit()

    # -- helpers ---------------------------------------------------------------

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
            raise ValueError(f"PipelineStep '{STEP_NAME}' not found for run {run_id}")
        return step

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_design_documents(
        self, project_id: uuid.UUID
    ) -> tuple[Document, Document, Document, Document, Document]:
        def _latest(doc_type: DocumentType) -> Document:
            doc = self.session.exec(
                select(Document)
                .where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                )
                .order_by(Document.created_at.desc())  # type: ignore[union-attr]
            ).first()
            if not doc:
                raise ValueError(f"No {doc_type.value} document found for project {project_id}")
            return doc

        fsd    = _latest(DocumentType.fsd)
        arch   = _latest(DocumentType.architecture_design)
        db     = _latest(DocumentType.database_design)
        api    = _latest(DocumentType.api_spec)
        screen = _latest(DocumentType.screen_spec)
        return fsd, arch, db, api, screen

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        self.session.add(ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.task_completed,
            message=message,
        ))
