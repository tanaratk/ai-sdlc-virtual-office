"""Solution Architect Agent — Pipeline Step 4.

Reads the approved BRD, FSD, and User Story Backlog and produces:
  - Architecture Design (system components, deployment, security, integrations)
  - Database Design (table spec, relationships)
  - API Specification (endpoints with request/response fields)
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

AGENT_NAME = "architect-agent"
STEP_NAME = "sa_documents"
TIMEOUT_SECONDS = 240.0


# ── Output schema ──────────────────────────────────────────────────────────────

class _Component(BaseModel):
    id: str = "COMP-001"
    name: str
    type: str = "service"
    technology: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    requirement_refs: list[str] = Field(default_factory=list)


class _IntegrationPoint(BaseModel):
    system: str
    protocol: str = "REST"
    description: str


class ArchitectureOutput(BaseModel):
    system_type: str = ""
    components: list[_Component] = Field(default_factory=list)
    deployment_notes: str = ""
    security_considerations: list[str] = Field(default_factory=list)
    integration_points: list[_IntegrationPoint] = Field(default_factory=list)


class _DBColumn(BaseModel):
    name: str
    type: str
    nullable: bool = True
    description: str = ""


class _DBTable(BaseModel):
    id: str = "DB-001"
    name: str
    description: str
    columns: list[_DBColumn] = Field(default_factory=list)
    requirement_ref: str = ""


class _DBRelationship(BaseModel):
    from_table: str
    to_table: str
    type: str = "one_to_many"
    description: str = ""


class DatabaseOutput(BaseModel):
    tables: list[_DBTable] = Field(default_factory=list)
    relationships: list[_DBRelationship] = Field(default_factory=list)


class _APIField(BaseModel):
    name: str
    type: str
    required: bool = True
    description: str = ""


class _APIEndpoint(BaseModel):
    id: str = "API-001"
    method: str = "GET"
    path: str
    description: str
    request_fields: list[_APIField] = Field(default_factory=list)
    response_fields: list[_APIField] = Field(default_factory=list)
    requirement_ref: str = ""


class APISpecOutput(BaseModel):
    base_url: str = "/api/v1"
    endpoints: list[_APIEndpoint] = Field(default_factory=list)


class SAAgentOutput(BaseModel):
    architecture: ArchitectureOutput = Field(default_factory=ArchitectureOutput)
    database: DatabaseOutput = Field(default_factory=DatabaseOutput)
    api_spec: APISpecOutput = Field(default_factory=APISpecOutput)


# ── Prompts ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are the Solution Architect Agent in an AI-powered software factory.
Your job is to read the BRD, FSD, and User Story Backlog and produce:
  1. Architecture Design (components, deployment, security, integrations)
  2. Database Design (tables with columns and relationships)
  3. API Specification (REST endpoints with request/response fields)

Rules:
- Every component must have a unique ID (COMP-001, COMP-002, …).
- Every database table must have a unique ID (DB-001, DB-002, …).
- Every API endpoint must have a unique ID (API-001, API-002, …).
- Every table and endpoint must reference a requirement ID (FR-XXX) in requirement_ref.
- Column types must be SQL-compatible (e.g., UUID, VARCHAR(255), DECIMAL(12,2), BOOLEAN).
- API methods must be one of: GET, POST, PUT, PATCH, DELETE.
- You MUST return ONLY a valid JSON object — no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following BA documents and produce an Architecture Design,
Database Design, and API Specification.
Return ONLY the JSON — no explanation, no code fences.

Schema:
{{
  "architecture": {{
    "system_type": "Web Application|Microservices|Mobile App|etc.",
    "components": [
      {{
        "id": "COMP-001",
        "name": "component name",
        "type": "frontend|backend|database|gateway|queue|cache|storage",
        "technology": "specific tech stack",
        "description": "what this component does",
        "responsibilities": ["responsibility 1"],
        "requirement_refs": ["FR-001"]
      }}
    ],
    "deployment_notes": "1-3 sentences on deployment approach",
    "security_considerations": ["security requirement 1"],
    "integration_points": [
      {{"system": "external system name", "protocol": "REST|SMTP|gRPC|etc.", "description": "how it integrates"}}
    ]
  }},
  "database": {{
    "tables": [
      {{
        "id": "DB-001",
        "name": "table_name",
        "description": "what this table stores",
        "columns": [
          {{"name": "column_name", "type": "SQL_TYPE", "nullable": false, "description": "field description"}}
        ],
        "requirement_ref": "FR-001"
      }}
    ],
    "relationships": [
      {{"from_table": "table_a", "to_table": "table_b", "type": "one_to_many|many_to_one|many_to_many|one_to_one", "description": "relationship description"}}
    ]
  }},
  "api_spec": {{
    "base_url": "/api/v1",
    "endpoints": [
      {{
        "id": "API-001",
        "method": "GET|POST|PUT|PATCH|DELETE",
        "path": "/resource/{{id}}",
        "description": "what this endpoint does",
        "request_fields": [
          {{"name": "field_name", "type": "string|number|boolean|object|array", "required": true, "description": "field description"}}
        ],
        "response_fields": [
          {{"name": "field_name", "type": "string|number|boolean|object|array", "required": true, "description": "field description"}}
        ],
        "requirement_ref": "FR-001"
      }}
    ]
  }}
}}

BUSINESS REQUIREMENTS DOCUMENT (BRD):
{brd}

FUNCTIONAL SPECIFICATION DOCUMENT (FSD):
{fsd}

USER STORY BACKLOG:
{user_stories}
"""


# ── Markdown renderers ─────────────────────────────────────────────────────────

def _render_architecture(data: ArchitectureOutput, project_id: str, doc_id: str) -> str:
    comp_section = ""
    for c in data.components:
        refs = ", ".join(c.requirement_refs) if c.requirement_refs else "—"
        resp = "\n".join(f"- {r}" for r in c.responsibilities) if c.responsibilities else "> Not specified."
        comp_section += f"""
### {c.id} — {c.name} ({c.type})

**Technology:** {c.technology}
**Requirement Refs:** {refs}

{c.description}

**Responsibilities:**

{resp}

---
"""

    sec_bullets = "\n".join(f"- {s}" for s in data.security_considerations) \
        if data.security_considerations else "> No security considerations specified."

    int_rows = ""
    for ip in data.integration_points:
        int_rows += f"| {ip.system} | {ip.protocol} | {ip.description} |\n"
    if not int_rows:
        int_rows = "| — | — | No integrations defined |\n"

    return f"""\
# Architecture Design

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Solution Architect Agent v1.0.0
**Pipeline Step:** 4 of 10
**Status:** Draft → Awaiting Review

---

## 1. System Type

{data.system_type or "> Not specified."}

---

## 2. Components
{comp_section if comp_section else "> No components defined."}

## 3. Deployment Notes

{data.deployment_notes or "> Not specified."}

---

## 4. Security Considerations

{sec_bullets}

---

## 5. Integration Points

| External System | Protocol | Description |
|---|---|---|
{int_rows}"""


def _render_database(data: DatabaseOutput, project_id: str, doc_id: str) -> str:
    tables_section = ""
    for t in data.tables:
        col_rows = ""
        for col in t.columns:
            null_str = "NULL" if col.nullable else "NOT NULL"
            col_rows += f"| `{col.name}` | {col.type} | {null_str} | {col.description} |\n"
        if not col_rows:
            col_rows = "| — | — | — | No columns defined |\n"
        ref = f" ← {t.requirement_ref}" if t.requirement_ref else ""
        tables_section += f"""
### {t.id}{ref} — `{t.name}`

{t.description}

| Column | Type | Nullable | Description |
|---|---|---|---|
{col_rows}
---
"""

    rel_rows = ""
    for r in data.relationships:
        rel_rows += f"| `{r.from_table}` | {r.type.replace('_', ' ')} | `{r.to_table}` | {r.description} |\n"
    if not rel_rows:
        rel_rows = "| — | — | — | No relationships defined |\n"

    return f"""\
# Database Design

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Solution Architect Agent v1.0.0
**Pipeline Step:** 4 of 10
**Status:** Draft → Awaiting Review

---

## 1. Tables
{tables_section if tables_section else "> No tables defined."}

## 2. Relationships

| From Table | Type | To Table | Description |
|---|---|---|---|
{rel_rows}"""


def _render_api_spec(data: APISpecOutput, project_id: str, doc_id: str) -> str:
    endpoints_section = ""
    for ep in data.endpoints:
        req_rows = ""
        for f in ep.request_fields:
            req_str = "required" if f.required else "optional"
            req_rows += f"| `{f.name}` | {f.type} | {req_str} | {f.description} |\n"
        res_rows = ""
        for f in ep.response_fields:
            req_str = "required" if f.required else "optional"
            res_rows += f"| `{f.name}` | {f.type} | {req_str} | {f.description} |\n"

        ref = f" ← {ep.requirement_ref}" if ep.requirement_ref else ""
        _req_hdr = "| Field | Type | Required | Description |\n|---|---|---|---|\n"
        _req_block = (_req_hdr + req_rows) if req_rows else "> No request body."
        _res_block = (_req_hdr + res_rows) if res_rows else "> No response fields defined."
        endpoints_section += f"""
### {ep.id}{ref} — `{ep.method} {data.base_url}{ep.path}`

{ep.description}

**Request Fields:**

{_req_block}

**Response Fields:**

{_res_block}

---
"""

    return f"""\
# API Specification

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Solution Architect Agent v1.0.0
**Pipeline Step:** 4 of 10
**Base URL:** `{data.base_url}`
**Status:** Draft → Awaiting Review
**Total Endpoints:** {len(data.endpoints)}

---
{endpoints_section if endpoints_section else "> No endpoints defined."}"""


# ── Agent runner ───────────────────────────────────────────────────────────────

class SAAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("SAAgent skipped — run %s already failed", run_id)
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

            brd_doc, fsd_doc, us_doc = self._load_ba_documents(run.project_id)

            raw_json = call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    brd=brd_doc.content_markdown,
                    fsd=fsd_doc.content_markdown,
                    user_stories=us_doc.content_markdown,
                ),
                timeout=TIMEOUT_SECONDS,
            )

            parsed = extract_json(raw_json)
            output = SAAgentOutput.model_validate(parsed)

            arch_id, db_id, api_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            pid = str(run.project_id)

            arch_doc = Document(
                id=arch_id,
                project_id=run.project_id,
                document_type=DocumentType.architecture_design,
                title="Architecture Design",
                content_markdown=_render_architecture(output.architecture, pid, str(arch_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            db_doc = Document(
                id=db_id,
                project_id=run.project_id,
                document_type=DocumentType.database_design,
                title="Database Design",
                content_markdown=_render_database(output.database, pid, str(db_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            api_doc = Document(
                id=api_id,
                project_id=run.project_id,
                document_type=DocumentType.api_spec,
                title="API Specification",
                content_markdown=_render_api_spec(output.api_spec, pid, str(api_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(arch_doc)
            self.session.add(db_doc)
            self.session.add(api_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = arch_doc.id  # Architecture is the primary output
            step.completed_at = datetime.utcnow()

            # Gate 3 — wait for human review of Architecture/DB/API
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.utcnow()

            self._log_activity(
                run.project_id, agent_row,
                f"SA documents created: Architecture ({len(output.architecture.components)} components), "
                f"Database ({len(output.database.tables)} tables), "
                f"API ({len(output.api_spec.endpoints)} endpoints). Awaiting Gate 3 review.",
            )
            self.session.commit()
            logger.info(
                "SAAgent completed run=%s arch=%s db=%s api=%s",
                run_id, arch_id, db_id, api_id,
            )

        except Exception as exc:
            logger.exception("SAAgent failed run=%s: %s", run_id, exc)
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

    def _load_ba_documents(self, project_id: uuid.UUID) -> tuple[Document, Document, Document]:
        def _latest(doc_type: DocumentType) -> Optional[Document]:
            return self.session.exec(
                select(Document).where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                ).order_by(Document.created_at.desc())
            ).first()

        brd = _latest(DocumentType.brd)
        fsd = _latest(DocumentType.fsd)
        us = _latest(DocumentType.user_story)
        if not brd or not fsd or not us:
            missing = [t for t, d in [("BRD", brd), ("FSD", fsd), ("User Story", us)] if not d]
            raise ValueError(f"Missing BA documents: {', '.join(missing)}")
        return brd, fsd, us

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
