"""Code Review Agent -- Pipeline Step 7 (Delivery Layer).

Scans the generated_app workspace directory, reads source files, and calls the
LLM to produce a structured code review report (code_review.md).

Verdict logic:
  PASS        -- 0 critical, 0 major issues
  NEEDS_WORK  -- 0 critical, >= 1 major issues
  FAIL        -- >= 1 critical issue
"""
import logging
import os
import re
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

AGENT_NAME = "code-review-agent"
STEP_NAME = "code_review"
TIMEOUT_SECONDS = 300.0

# Max bytes of code content to send to LLM (avoid context overflow)
_MAX_CODE_BYTES = 80_000

# Text file extensions to include in review
_TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json",
    ".yaml", ".yml", ".toml", ".md", ".sh", ".sql", ".env.example",
    ".Dockerfile", "",  # extensionless files like Dockerfile, Makefile
}

_BINARY_PREFIXES = (".", "__pycache__", "node_modules", ".git", "dist", "build")


# -- Output schema -------------------------------------------------------------

class _Issue(BaseModel):
    id: str = "CR-001"
    severity: str = "minor"
    file: str = ""
    line_approximate: int = 0
    issue: str = ""
    suggestion: str = ""
    category: str = "style"

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if not isinstance(v, dict):
            return v
        if not v.get("id"):
            v["id"] = "CR-001"
        sev = str(v.get("severity", "minor")).lower()
        if sev not in {"critical", "major", "minor", "info"}:
            sev = "minor"
        v["severity"] = sev
        cat = str(v.get("category", "style")).lower()
        if cat not in {"security", "performance", "logic", "style", "completeness"}:
            cat = "style"
        v["category"] = cat
        try:
            v["line_approximate"] = int(v.get("line_approximate", 0))
        except (TypeError, ValueError):
            v["line_approximate"] = 0
        return v


class CodeReviewOutput(BaseModel):
    overall_status: str = "PASS"
    summary: str = ""
    issues: list[_Issue] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _derive_status(cls, v: dict) -> dict:
        if not isinstance(v, dict):
            return v
        issues = v.get("issues", [])
        criticals = sum(1 for i in issues if isinstance(i, dict) and i.get("severity") == "critical")
        majors = sum(1 for i in issues if isinstance(i, dict) and i.get("severity") == "major")
        if criticals > 0:
            v["overall_status"] = "FAIL"
        elif majors > 0:
            v["overall_status"] = "NEEDS_WORK"
        else:
            v["overall_status"] = "PASS"
        if not v.get("summary"):
            v["summary"] = f"{len(issues)} issues found: {criticals} critical, {majors} major."
        return v


# -- Prompts -------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are the Code Review Agent in an AI-powered software factory.
Your job is to review generated source code and produce a structured report.

Rules:
- Every issue must have a unique ID: CR-001, CR-002, ...
- severity must be one of: critical, major, minor, info
- category must be one of: security, performance, logic, style, completeness
- file is the relative path from generated_app root
- line_approximate is your best guess at the line number (0 if unknown)
- Focus on: security vulnerabilities, missing error handling, hardcoded secrets,
  SQL injection, XSS, incomplete implementations, broken imports, missing tests
- Completeness: check that each TASK mentioned was actually implemented
- You MUST return ONLY a valid JSON object -- no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Review the following generated source code and produce a code review report.
Return ONLY the JSON -- no explanation, no code fences.

Schema:
{{
  "summary": "One-paragraph summary of the code quality and main findings.",
  "issues": [
    {{
      "id": "CR-001",
      "severity": "critical|major|minor|info",
      "file": "relative/path/to/file.py",
      "line_approximate": 42,
      "issue": "Description of what is wrong",
      "suggestion": "How to fix it",
      "category": "security|performance|logic|style|completeness"
    }}
  ]
}}

--- TASK LIST (expected implementations) ---
{dev_tasks}

--- GENERATED CODE ---
{code_content}
"""


# -- File scanner --------------------------------------------------------------

def _collect_code(app_dir: str) -> tuple[str, int]:
    """Walk generated_app dir, collect text files up to _MAX_CODE_BYTES.

    Returns (concatenated_content, file_count).
    """
    parts: list[str] = []
    total_bytes = 0
    file_count = 0

    for root, dirs, files in os.walk(app_dir):
        # prune binary/cache directories
        dirs[:] = [
            d for d in sorted(dirs)
            if not any(d.startswith(p) for p in _BINARY_PREFIXES)
        ]
        for fname in sorted(files):
            if any(fname.startswith(p) for p in _BINARY_PREFIXES):
                continue
            _, ext = os.path.splitext(fname)
            if ext.lower() not in _TEXT_EXTENSIONS and ext != "":
                continue

            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, app_dir)

            try:
                with open(full_path, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue

            snippet = f"\n### {rel_path}\n```\n{content[:3000]}\n```\n"
            snippet_bytes = len(snippet.encode("utf-8"))

            if total_bytes + snippet_bytes > _MAX_CODE_BYTES:
                parts.append(f"\n### (truncated — size limit reached)\n")
                break
            parts.append(snippet)
            total_bytes += snippet_bytes
            file_count += 1
        else:
            continue
        break

    if not parts:
        return "(no generated code found)", 0

    return "".join(parts), file_count


# -- Renderers -----------------------------------------------------------------

def _verdict_emoji(status: str) -> str:
    return {"PASS": "PASS", "NEEDS_WORK": "NEEDS WORK", "FAIL": "FAIL"}.get(status, status)


def _render_review(output: CodeReviewOutput, file_count: int, doc_id: str) -> str:
    severity_order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    sorted_issues = sorted(output.issues, key=lambda i: severity_order.get(i.severity, 9))

    counts = {s: 0 for s in ("critical", "major", "minor", "info")}
    for i in sorted_issues:
        counts[i.severity] = counts.get(i.severity, 0) + 1

    issue_rows = "\n".join(
        f"| {i.id} | {i.severity.upper()} | `{i.file}` | ~{i.line_approximate} | "
        f"{i.category} | {i.issue[:60]} |"
        for i in sorted_issues
    )

    detail_blocks = ""
    for i in sorted_issues:
        detail_blocks += f"""
### {i.id} [{i.severity.upper()}] — {i.issue}

| Field | Value |
|-------|-------|
| File | `{i.file}` |
| Line | ~{i.line_approximate} |
| Category | {i.category} |
| Severity | **{i.severity}** |

**Suggestion:** {i.suggestion}

"""

    return f"""\
# Code Review Report

> **Document ID:** CR-{doc_id[:8]}
> **Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}
> **Files reviewed:** {file_count}

## Verdict: {_verdict_emoji(output.overall_status)}

## Summary

{output.summary}

## Statistics

| Severity | Count |
|----------|-------|
| Critical | {counts['critical']} |
| Major    | {counts['major']} |
| Minor    | {counts['minor']} |
| Info     | {counts['info']} |
| **Total**| **{len(sorted_issues)}** |

> **Verdict rules:**
> - PASS: 0 critical + 0 major
> - NEEDS WORK: 0 critical + ≥ 1 major
> - FAIL: ≥ 1 critical

## Issues

| ID | Severity | File | Line | Category | Description |
|----|----------|------|------|----------|-------------|
{issue_rows}

## Issue Details
{detail_blocks}
"""


# -- Runner --------------------------------------------------------------------

class CodeReviewAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("CodeReviewAgent skipped -- run %s already failed", run_id)
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

            # Load dev_tasks.md from DB for completeness check
            dev_tasks_doc = self._load_dev_tasks(run.project_id)
            dev_tasks_content = dev_tasks_doc.content_markdown if dev_tasks_doc else "(not available)"

            # Scan generated code from workspace
            app_dir = self._get_app_dir(run.project_id)
            code_content, file_count = _collect_code(app_dir)
            logger.info("CodeReviewAgent scanning %s files in %s", file_count, app_dir)

            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    dev_tasks=dev_tasks_content[:5000],
                    code_content=code_content,
                ),
                model=agent_row.model_name if agent_row else None,
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = CodeReviewOutput.model_validate(parsed)

            doc_id = uuid.uuid4()
            markdown = _render_review(output, file_count, str(doc_id))

            doc = Document(
                id=doc_id,
                project_id=run.project_id,
                document_type=DocumentType.code_review,
                title=f"Code Review — {output.overall_status} ({len(output.issues)} issues)",
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

            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            critical_count = sum(1 for i in output.issues if i.severity == "critical")
            self._log_activity(
                run.project_id, agent_row,
                f"Code review complete: {output.overall_status}. "
                f"{len(output.issues)} issues ({critical_count} critical). "
                f"{file_count} files reviewed.",
            )
            self.session.commit()

            from app.agents._workspace import write_workspace_docs
            write_workspace_docs(self.session, run.project_id, {"code_review.md": markdown})
            logger.info(
                "CodeReviewAgent completed run=%s doc=%s verdict=%s issues=%d",
                run_id, doc_id, output.overall_status, len(output.issues),
            )

        except Exception as exc:
            logger.exception("CodeReviewAgent failed run=%s: %s", run_id, exc)
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

    def _load_dev_tasks(self, project_id: uuid.UUID) -> Optional[Document]:
        return self.session.exec(
            select(Document)
            .where(
                Document.project_id == project_id,
                Document.document_type == DocumentType.technical_design,
            )
            .order_by(Document.created_at.desc())  # type: ignore[union-attr]
        ).first()

    def _get_app_dir(self, project_id: uuid.UUID) -> str:
        project = self.session.get(Project, project_id)
        raw = (project.workspace_path if project else None) or "/workspace"

        container_path = re.sub(
            r"^[A-Za-z]:[/\\]workspace", "/workspace", raw, flags=re.IGNORECASE
        )
        if not container_path.startswith("/workspace"):
            container_path = "/workspace"

        safe_name = re.sub(r"[^\w\-]", "_", project.name if project else "project")
        return os.path.join(container_path, safe_name, "generated_app")

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        self.session.add(ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.agent_completed,
            message=message,
        ))
