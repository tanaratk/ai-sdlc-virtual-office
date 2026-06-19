"""Developer Agent -- Pipeline Step 6.

Reads the approved FSD, Architecture Design, Database Design, API Spec,
and Screen Specification to generate real source code files for the project.

Generation strategy (2-phase):
  Phase 1 -- Planning call (JSON): decide which files to create and their purposes.
  Phase 2 -- Per-file call (text): generate raw code for each file.

Files are written to: {workspace}/generated_app/{file_path}
A summary document (code_task_list type) is saved to the DB.
"""
import logging
import os
import re
import uuid
from datetime import UTC, datetime
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
    Project,
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "developer-agent"
STEP_NAME = "dev_tasks"

PLAN_TIMEOUT = 120.0
FILE_TIMEOUT = 120.0
MAX_FILES = 20
MIN_FILE_CHARS = 30


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


def _trunc(s: str, n: int) -> str:
    return s[:n] + "\n...(truncated)" if len(s) > n else s


# -- File plan schema ---------------------------------------------------------

class _FileSpec(BaseModel):
    path: str = ""
    lang: str = "python"
    purpose: str = ""
    context_hint: str = "backend"

    class Config:
        extra = "ignore"


class _FilePlan(BaseModel):
    files: list[_FileSpec] = Field(default_factory=list)

    class Config:
        extra = "ignore"


# -- Prompts ------------------------------------------------------------------

_PLAN_SYSTEM_PROMPT = """\
You are a senior software architect in an AI-powered software factory.
Given technical specification documents, decide which source code files \
to generate for a full-stack web application.

RULES:
- Produce a JSON object with a "files" array only.
- Each file must have: path, lang, purpose, context_hint.
- path: relative path inside the project (e.g. "backend/app/models/user.py")
- lang: "python", "typescript", "sql", "yaml", "markdown", or "text"
- purpose: one sentence describing what this file does
- context_hint: one of "backend_model", "backend_route", "backend_schema",
  "backend_migration", "frontend_type", "frontend_service",
  "frontend_component", "frontend_page", "readme"
- Generate at most 15 files. Focus on the most critical files first.
- Include: models, routes, schemas, one migration, key frontend pages/types/services, README.
- Do NOT generate test files or config files in this phase.
- Return ONLY valid JSON. No markdown fences, no explanation.
"""

_PLAN_TEMPLATE = """\
Generate the file plan for this project. Return JSON only.

FUNCTIONAL SPECIFICATION (excerpt):
{fsd}

DATABASE DESIGN (excerpt):
{database}

API SPECIFICATION (excerpt):
{api_spec}

SCREEN SPECIFICATION (excerpt):
{screen_spec}

Schema:
{{
  "files": [
    {{
      "path": "backend/app/models/user.py",
      "lang": "python",
      "purpose": "SQLModel User table definition",
      "context_hint": "backend_model"
    }}
  ]
}}
"""

_FILE_SYSTEM_PROMPT = """\
You are an expert code generator. You write clean, production-ready code.

RULES:
- Output ONLY the file content. No markdown fences. No explanation. No comments \
  unless the code logic requires it.
- Write complete, runnable code — not stubs or placeholders.
- Follow the tech stack: FastAPI + SQLModel + PostgreSQL for backend, \
  React + TypeScript + Vite + Tailwind for frontend.
- Use standard patterns: Pydantic models, SQLModel tables, FastAPI APIRouter, \
  React functional components with hooks.
- Never output TODO or pass-only stubs unless the file is intentionally minimal.
"""

_FILE_TEMPLATE = """\
Generate the complete content of this file:

FILE PATH: {path}
LANGUAGE: {lang}
PURPOSE: {purpose}

RELEVANT SPECIFICATION:
{context}

Output the file content directly. No fences, no explanation.
"""

# Context snippets per hint type
_CONTEXT_CHARS = {
    "backend_model":     ("database", 4000),
    "backend_schema":    ("api_spec", 3000),
    "backend_route":     ("api_spec", 4000),
    "backend_migration": ("database", 3000),
    "frontend_type":     ("api_spec", 3000),
    "frontend_service":  ("api_spec", 3500),
    "frontend_component":("screen_spec", 3500),
    "frontend_page":     ("screen_spec", 4000),
    "readme":            ("fsd", 2000),
}


# -- Markdown renderer for summary document -----------------------------------

def _render_summary(
    files: list[_FileSpec],
    results: list[tuple[str, bool]],
    project_id: str,
    doc_id: str,
) -> str:
    ok = sum(1 for _, success in results if success)
    fail = len(results) - ok

    rows = ""
    for spec, (_, success) in zip(files, results):
        status = "OK" if success else "FAILED"
        rows += f"| `{spec.path}` | {spec.lang} | {spec.purpose[:60]} | {status} |\n"

    return f"""\
# Generated Code Summary

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Developer Agent v2.0.0
**Pipeline Step:** 6 of 10
**Status:** Draft -- Awaiting Review

---

## Generation Results

| Files OK | Files Failed |
|---|---|
| {ok} | {fail} |

## File List

| Path | Language | Purpose | Status |
|---|---|---|---|
{rows}

---

## Output Location

Files are written to: `generated_app/` inside the project workspace.

{"**Warning:** Some files failed to generate. Review and regenerate manually." if fail else "All files generated successfully."}
"""


# -- Agent runner -------------------------------------------------------------

class DevAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("DevAgent skipped -- run %s already failed", run_id)
                return

            step = self._get_step(run_id)
            agent_row = self._get_agent_row()
            model = agent_row.model_name if agent_row else None

            run.status = PipelineRunStatus.running
            run.current_step = STEP_NAME
            step.status = PipelineStepStatus.running
            step.started_at = datetime.now(UTC)
            if agent_row:
                agent_row.status = AgentStatus.working
                agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

            fsd_doc, arch_doc, db_doc, api_doc, screen_doc = \
                self._load_source_documents(run.project_id)

            docs = {
                "fsd":        fsd_doc.content_markdown,
                "architecture": arch_doc.content_markdown,
                "database":   db_doc.content_markdown,
                "api_spec":   api_doc.content_markdown,
                "screen_spec": screen_doc.content_markdown,
            }

            # Phase 1: plan which files to generate
            file_plan = self._plan_files(docs, model)
            files = file_plan.files[:MAX_FILES]
            logger.info("DevAgent planned %d files for run=%s", len(files), run_id)

            # Phase 2: generate each file
            out_dir = self._get_output_dir(run.project_id)
            results: list[tuple[str, bool]] = []
            for spec in files:
                content = self._generate_file(spec, docs, model)
                if content:
                    self._write_file(out_dir, spec.path, content)
                    results.append((spec.path, True))
                    logger.info("DevAgent generated %s", spec.path)
                else:
                    results.append((spec.path, False))
                    logger.warning("DevAgent failed to generate %s", spec.path)

            # Save summary document
            doc_id = uuid.uuid4()
            pid = str(run.project_id)
            summary_md = _render_summary(files, results, pid, str(doc_id))

            summary_doc = Document(
                id=doc_id,
                project_id=run.project_id,
                document_type=DocumentType.code_task_list,
                title="Generated Code Summary",
                content_markdown=summary_md,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(summary_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = summary_doc.id
            step.completed_at = datetime.now(UTC)

            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            ok_count = sum(1 for _, s in results if s)
            self._log_activity(
                run.project_id, agent_row,
                f"Code generation complete: {ok_count}/{len(files)} files generated "
                f"to generated_app/. Awaiting Gate 5 review.",
            )
            self.session.commit()
            logger.info(
                "DevAgent completed run=%s files=%d/%d",
                run_id, ok_count, len(files),
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
                    agent_row.updated_at = datetime.now(UTC)
                self.session.commit()
            except Exception:
                logger.exception("Failed to persist failure state for run=%s", run_id)

    # -- Generation helpers ---------------------------------------------------

    def _plan_files(self, docs: dict[str, str], model: str | None) -> _FilePlan:
        prompt = _PLAN_TEMPLATE.format(
            fsd=_esc(_trunc(docs["fsd"], 3000)),
            database=_esc(_trunc(docs["database"], 3000)),
            api_spec=_esc(_trunc(docs["api_spec"], 3000)),
            screen_spec=_esc(_trunc(docs["screen_spec"], 2000)),
        )
        raw = _llm.call_ollama(
            system_prompt=_PLAN_SYSTEM_PROMPT,
            user_prompt=prompt,
            model=model,
            timeout=PLAN_TIMEOUT,
            response_format="json",
        )
        data = _llm.extract_json(raw)
        return _FilePlan.model_validate(data)

    def _generate_file(
        self,
        spec: _FileSpec,
        docs: dict[str, str],
        model: str | None,
    ) -> str | None:
        context = self._build_context(spec, docs)
        prompt = _FILE_TEMPLATE.format(
            path=spec.path,
            lang=spec.lang,
            purpose=spec.purpose,
            context=context,
        )
        for attempt in range(2):
            try:
                raw = _llm.call_ollama(
                    system_prompt=_FILE_SYSTEM_PROMPT,
                    user_prompt=prompt,
                    model=model,
                    timeout=FILE_TIMEOUT,
                    response_format=None,
                )
                content = _llm.strip_code_fences(raw)
                if len(content) >= MIN_FILE_CHARS:
                    return content
                logger.warning(
                    "File %s: content too short (%d chars), attempt %d",
                    spec.path, len(content), attempt + 1,
                )
            except Exception as exc:
                logger.warning(
                    "File %s generation error (attempt %d): %s",
                    spec.path, attempt + 1, exc,
                )
        return None

    def _build_context(self, spec: _FileSpec, docs: dict[str, str]) -> str:
        hint = spec.context_hint
        mapping = _CONTEXT_CHARS.get(hint, ("fsd", 2000))
        primary_key, primary_chars = mapping

        primary = _trunc(docs.get(primary_key, ""), primary_chars)

        # Add FSD excerpt as secondary context for all non-readme types
        secondary = ""
        if hint not in ("readme",) and primary_key != "fsd":
            secondary = f"\n\nFSD EXCERPT:\n{_trunc(docs['fsd'], 1500)}"

        return primary + secondary

    def _write_file(self, out_dir: str, rel_path: str, content: str) -> None:
        # Sanitise path — strip leading slashes and prevent traversal
        safe_rel = re.sub(r"\.\.+[/\\]", "", rel_path).lstrip("/\\")
        full_path = os.path.join(out_dir, safe_rel)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _get_output_dir(self, project_id: uuid.UUID) -> str:
        project = self.session.get(Project, project_id)
        raw_path = (project.workspace_path if project else None) or "/workspace"

        container_path = re.sub(
            r"^[A-Za-z]:[/\\]workspace", "/workspace", raw_path, flags=re.IGNORECASE
        )
        if not container_path.startswith("/workspace"):
            container_path = "/workspace"

        safe_name = re.sub(r"[^\w\-]", "_", project.name if project else "project")
        return os.path.join(container_path, safe_name, "generated_app")

    # -- DB helpers -----------------------------------------------------------

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

    def _log_activity(
        self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str
    ) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
