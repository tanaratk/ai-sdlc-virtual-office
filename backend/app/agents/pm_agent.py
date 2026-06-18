"""PM Agent — Pipeline Step 10 (final step).

Reads project metadata and all available documents, calls the LLM to
produce an executive-level Project Summary, then assembles a data-driven
Delivery Report from DB records.  Two documents are saved:
  - project_summary  (LLM-generated narrative + scope table)
  - delivery_report  (DB-driven: pipeline log, document inventory, quality metrics)
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import Session, func, select

from app.db.models import (
    ActivityLog,
    Agent,
    AgentStatus,
    Document,
    DocumentStatus,
    DocumentType,
    EventType,
    PipelineRun,
    PipelineStep,
    TraceabilityLink,
)
from app.llm.client import call_ollama, extract_json

logger = logging.getLogger(__name__)

AGENT_NAME = "pm-agent"
TIMEOUT_SECONDS = 180.0


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


# ── LLM output schema ──────────────────────────────────────────────────────────

class _ScopeItem(BaseModel):
    item: str
    status: str = "Delivered"


class _Risk(BaseModel):
    risk: str
    likelihood: str = "Medium"
    impact: str = "Medium"
    mitigation: str


class PMSummaryOutput(BaseModel):
    executive_summary: str
    scope_delivered: list[_ScopeItem] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    risks: list[_Risk] = Field(default_factory=list)


# ── Prompts ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are the PM Agent — the final step in an AI-powered software factory pipeline.
Your job is to write a concise, professional Project Summary for stakeholders.

RULES:
- Base your output ONLY on the information provided — do not invent requirements.
- executive_summary: 2–3 paragraphs suitable for executive review.
- scope_delivered: list each major deliverable (not individual FRs — group by theme).
- next_steps: 3–5 actionable items for the team after this pipeline run.
- risks: real risks derived from the requirement context — not fabricated.
- Return ONLY a valid JSON object — no markdown, no prose outside JSON.
"""

_TASK_TEMPLATE = """\
Write the PM-level project summary for this project.

PROJECT: {project_name}
DOCUMENTS PRODUCED: {doc_count}
TRACEABILITY LINKS: {trace_count}

REQUIREMENT SUMMARY (key context):
{req_summary}

Return ONLY this JSON schema:
{{
  "executive_summary": "2-3 paragraph executive summary...",
  "scope_delivered": [
    {{"item": "Requirement Analysis & Gap Detection", "status": "Delivered"}},
    {{"item": "Business Requirements & Functional Specification", "status": "Delivered"}}
  ],
  "next_steps": [
    "Review and approve all documents in the Documents panel",
    "Assign development tasks from the Code Task List to the team"
  ],
  "risks": [
    {{"risk": "...", "likelihood": "Medium", "impact": "High", "mitigation": "..."}}
  ]
}}
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

class _DocRow:
    def __init__(self, doc: Document) -> None:
        self.doc_type = doc.document_type
        self.title = doc.title
        self.version = doc.version
        self.status = doc.status
        self.approved_by = doc.approved_by or "—"
        self.doc_id = str(doc.id)
        self.created_at = doc.created_at.strftime("%Y-%m-%d")


class _StepRow:
    def __init__(self, step: PipelineStep, order: int) -> None:
        self.order = order
        self.step_name = step.step_name
        self.status = step.status
        self.started = step.started_at.strftime("%Y-%m-%d %H:%M") if step.started_at else "—"
        self.completed = step.completed_at.strftime("%Y-%m-%d %H:%M") if step.completed_at else "—"
        self.retry_count = step.retry_count

        if step.started_at and step.completed_at:
            secs = int((step.completed_at - step.started_at).total_seconds())
            self.duration = f"{secs // 60}m {secs % 60}s"
        else:
            self.duration = "—"


# ── Renderers ──────────────────────────────────────────────────────────────────

def _render_project_summary(
    output: PMSummaryOutput,
    project_name: str,
    project_id: str,
    doc_id: str,
    doc_rows: list[_DocRow],
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    scope_rows = "".join(
        f"| {s.item} | {s.status} |\n"
        for s in output.scope_delivered
    ) or "| — | — |\n"

    artifact_rows = "".join(
        f"| {r.doc_type} | {r.title} | {r.version} | {r.status} | {r.approved_by} |\n"
        for r in doc_rows
    ) or "| — | — | — | — | — |\n"

    next_steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(output.next_steps)) \
        or "> No next steps specified."

    risk_rows = "".join(
        f"| {r.risk} | {r.likelihood} | {r.impact} | {r.mitigation} |\n"
        for r in output.risks
    ) or "| — | — | — | — |\n"

    return f"""\
# Project Summary — {project_name}

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** PM Agent v1.0.0
**Pipeline Step:** 10 of 10 (Final)
**Generated At:** {now}
**Status:** Draft — Awaiting Review

---

## 1. Executive Summary

{output.executive_summary}

---

## 2. Scope Delivered

| Deliverable | Status |
|---|---|
{scope_rows}

---

## 3. Artifacts Produced

| Document Type | Title | Version | Status | Approved By |
|---|---|---|---|---|
{artifact_rows}

---

## 4. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
{risk_rows}

---

## 5. Next Steps

{next_steps}

---

*Generated by PM Agent v1.0.0 | {now}*
"""


def _render_delivery_report(
    project_name: str,
    project_id: str,
    doc_id: str,
    pipeline_run: Optional[PipelineRun],
    step_rows: list[_StepRow],
    doc_rows: list[_DocRow],
    trace_count: int,
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    run_id = str(pipeline_run.id) if pipeline_run else "—"
    started = pipeline_run.started_at.strftime("%Y-%m-%d %H:%M") \
        if pipeline_run and pipeline_run.started_at else "—"
    completed = pipeline_run.completed_at.strftime("%Y-%m-%d %H:%M") \
        if pipeline_run and pipeline_run.completed_at else "—"

    if pipeline_run and pipeline_run.started_at and pipeline_run.completed_at:
        total_secs = int((pipeline_run.completed_at - pipeline_run.started_at).total_seconds())
        duration = f"{total_secs // 3600}h {(total_secs % 3600) // 60}m"
    else:
        duration = "—"

    step_table = "".join(
        f"| {s.order} | {s.step_name} | {s.started} | {s.completed} "
        f"| {s.duration} | {s.retry_count} | {s.status} |\n"
        for s in step_rows
    ) or "| — | — | — | — | — | — | — |\n"

    doc_table = "".join(
        f"| {r.doc_type} | {r.title} | {r.version} | {r.status} "
        f"| {r.approved_by} | {r.created_at} |\n"
        for r in doc_rows
    ) or "| — | — | — | — | — | — |\n"

    total_retries = sum(s.retry_count for s in step_rows)
    approved_count = sum(1 for r in doc_rows if r.status == DocumentStatus.approved)

    return f"""\
# Delivery Report — {project_name}

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** PM Agent v1.0.0
**Pipeline Step:** 10 of 10 (Final)
**Generated At:** {now}
**Status:** Draft — Awaiting Sign-Off

---

## 1. Project Information

| Field | Value |
|---|---|
| Project | {project_name} |
| Project ID | `{project_id}` |
| Pipeline Run ID | `{run_id}` |
| Pipeline Started | {started} |
| Pipeline Completed | {completed} |
| Total Duration | {duration} |
| Total Steps Logged | {len(step_rows)} |
| Total Documents | {len(doc_rows)} |
| Approved Documents | {approved_count} |

---

## 2. Pipeline Execution Log

| # | Step Name | Started | Completed | Duration | Retries | Status |
|---|---|---|---|---|---|---|
{step_table}

**Total retries:** {total_retries}

---

## 3. Document Inventory

| Document Type | Title | Version | Status | Approved By | Created |
|---|---|---|---|---|---|
{doc_table}

---

## 4. Quality Metrics

| Metric | Value |
|---|---|
| Total Documents Produced | {len(doc_rows)} |
| Approved Documents | {approved_count} |
| Traceability Links | {trace_count} |
| Pipeline Steps Logged | {len(step_rows)} |
| Steps with Retries | {sum(1 for s in step_rows if s.retry_count > 0)} |
| Total Retries | {total_retries} |

---

## 5. Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Product Manager | | | |
| Business Analyst | | | |
| Solution Architect | | | |
| QA Lead | | | |
| Project Sponsor | | | |

---

*Generated by PM Agent v1.0.0 | {now}*
*Pipeline run complete. All documents available in the Documents panel.*
"""


# ── Agent runner ───────────────────────────────────────────────────────────────

class PMAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(
        self, project_id: uuid.UUID, project_name: str
    ) -> tuple[Document, Document]:
        """Returns (project_summary_doc, delivery_report_doc)."""
        agent_row = self._get_agent_row()

        if agent_row:
            agent_row.status = AgentStatus.working
            agent_row.updated_at = datetime.utcnow()
            self.session.commit()

        try:
            doc_rows = self._load_doc_rows(project_id)
            if not doc_rows:
                raise ValueError(
                    "No documents found for this project. "
                    "Run at least one pipeline agent before generating the PM summary."
                )

            pipeline_run, step_rows = self._load_pipeline_data(project_id)
            trace_count = self._count_traceability(project_id)
            req_summary = self._get_req_summary(doc_rows)

            pm_output = self._call_llm(project_name, len(doc_rows), trace_count, req_summary)

            pid = str(project_id)
            now = datetime.utcnow()

            # ── project_summary ───────────────────────────────────────────────
            ps_id = uuid.uuid4()
            ps_doc = Document(
                id=ps_id,
                project_id=project_id,
                document_type=DocumentType.project_summary,
                title=f"Project Summary — {project_name}",
                content_markdown=_render_project_summary(
                    pm_output, project_name, pid, str(ps_id), doc_rows
                ),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(ps_doc)

            # ── delivery_report ───────────────────────────────────────────────
            dr_id = uuid.uuid4()
            dr_doc = Document(
                id=dr_id,
                project_id=project_id,
                document_type=DocumentType.delivery_report,
                title=f"Delivery Report — {project_name}",
                content_markdown=_render_delivery_report(
                    project_name, pid, str(dr_id),
                    pipeline_run, step_rows, doc_rows, trace_count,
                ),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(dr_doc)

            self.session.add(ActivityLog(
                project_id=project_id,
                agent_id=agent_row.id if agent_row else None,
                event_type=EventType.document_created,
                message=(
                    f"PM Agent completed. Project Summary and Delivery Report created "
                    f"for '{project_name}'. {len(doc_rows)} document(s) inventoried. "
                    f"{trace_count} traceability link(s). Pipeline step 10 of 10 complete."
                ),
            ))

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = now

            self.session.commit()
            self.session.refresh(ps_doc)
            self.session.refresh(dr_doc)

            logger.info(
                "PMAgent completed project=%s ps=%s dr=%s docs=%d",
                project_id, ps_id, dr_id, len(doc_rows),
            )
            return ps_doc, dr_doc

        except Exception as exc:
            logger.exception("PMAgent failed project=%s: %s", project_id, exc)
            self.session.rollback()
            if agent_row:
                try:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.utcnow()
                    self.session.commit()
                except Exception:
                    pass
            raise

    # ── helpers ────────────────────────────────────────────────────────────────

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_doc_rows(self, project_id: uuid.UUID) -> list[_DocRow]:
        docs = self.session.exec(
            select(Document).where(
                Document.project_id == project_id,
            ).order_by(Document.created_at)
        ).all()
        return [_DocRow(d) for d in docs]

    def _get_req_summary(self, doc_rows: list[_DocRow]) -> str:
        """Pull req_summary content from already-loaded doc rows — avoids extra query."""
        for row in doc_rows:
            if row.doc_type == DocumentType.requirement_summary:
                # We need the full doc for content — do a targeted query
                break
        doc = self.session.exec(
            select(Document).where(
                Document.document_type == DocumentType.requirement_summary,
            ).order_by(Document.created_at.desc())
        ).first()
        return doc.content_markdown[:3000] if doc else ""

    def _load_pipeline_data(
        self, project_id: uuid.UUID
    ) -> tuple[Optional[PipelineRun], list[_StepRow]]:
        run = self.session.exec(
            select(PipelineRun).where(
                PipelineRun.project_id == project_id,
            ).order_by(PipelineRun.created_at.desc())
        ).first()

        if not run:
            return None, []

        steps = self.session.exec(
            select(PipelineStep).where(
                PipelineStep.pipeline_run_id == run.id,
            ).order_by(PipelineStep.started_at)
        ).all()
        return run, [_StepRow(s, i + 1) for i, s in enumerate(steps)]

    def _count_traceability(self, project_id: uuid.UUID) -> int:
        result = self.session.exec(
            select(func.count(TraceabilityLink.id)).where(
                TraceabilityLink.project_id == project_id
            )
        ).one()
        return result or 0

    def _call_llm(
        self,
        project_name: str,
        doc_count: int,
        trace_count: int,
        req_summary: str,
    ) -> PMSummaryOutput:
        prompt = _TASK_TEMPLATE.format(
            project_name=_esc(project_name),
            doc_count=doc_count,
            trace_count=trace_count,
            req_summary=_esc(req_summary) if req_summary else "(not available)",
        )
        raw = call_ollama(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=prompt,
            timeout=TIMEOUT_SECONDS,
        )
        parsed = extract_json(raw)
        return PMSummaryOutput.model_validate(parsed)
