"""BA Agent -- Pipeline Step 3.

Produces three documents from the approved requirement_summary + gap_analysis_report:
  - Business Requirements Document (BRD)
  - Functional Specification Document (FSD)
  - User Story Backlog
"""
import logging
import uuid
from datetime import UTC, datetime

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
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "ba-agent"
STEP_NAME = "ba_documents"
TIMEOUT_SECONDS = 180.0

# โ"€โ"€ Output schema โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

def _first(data: dict, *keys: str, fallback: str = "") -> str:
    for k in keys:
        if k in data and data[k]:
            return str(data[k])
    return fallback


class _BRDRisk(BaseModel):
    id: str = "RISK-001"
    description: str = ""
    impact: str = "Medium"

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("description"):
                v["description"] = _first(v, "text", "detail", "risk", "summary", fallback="")
        return v


class _BRDOutput(BaseModel):
    business_need: str = ""
    objectives: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risks: list[_BRDRisk] = Field(default_factory=list)


class _FSDSpec(BaseModel):
    id: str = "FSD-001"
    requirement_ref: str = ""
    feature: str = ""
    description: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("feature"):
                v["feature"] = _first(v, "name", "title", "feature_name", "spec_name", fallback="Feature")
            if not v.get("description"):
                v["description"] = _first(v, "detail", "summary", "spec", "specification", fallback="")
            if not v.get("requirement_ref"):
                v["requirement_ref"] = _first(v, "req_ref", "fr_ref", "requirement_id", fallback="")
        return v


class _FSDOutput(BaseModel):
    system_overview: str = ""
    functional_specs: list[_FSDSpec] = Field(default_factory=list)


class _UserStory(BaseModel):
    id: str = "US-001"
    requirement_ref: str = ""
    as_a: str = ""
    i_want: str = ""
    so_that: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    priority: str = "Must Have"

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("as_a"):
                v["as_a"] = _first(v, "role", "user", "persona", "actor", "as", fallback="User")
            if not v.get("i_want"):
                v["i_want"] = _first(v, "want", "need", "goal", "action", "feature", "i_want_to", fallback="")
            if not v.get("so_that"):
                v["so_that"] = _first(v, "benefit", "reason", "purpose", "value", "outcome", "so_that_i_can", fallback="")
            if not v.get("requirement_ref"):
                v["requirement_ref"] = _first(v, "req_ref", "fr_ref", "requirement_id", fallback="")
        return v


class BAAgentOutput(BaseModel):
    brd: _BRDOutput = Field(default_factory=_BRDOutput)
    fsd: _FSDOutput = Field(default_factory=_FSDOutput)
    user_stories: list[_UserStory] = Field(default_factory=list)


# โ"€โ"€ Prompts โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

_SYSTEM_PROMPT = """\
You are the BA Agent (Business Analyst Agent) in an AI-powered software factory.
Your job is to analyze a Requirement Summary and Gap Analysis Report and produce:
  1. A Business Requirements Document (BRD)
  2. A Functional Specification Document (FSD)
  3. A User Story Backlog

Rules:
- Base everything strictly on the provided documents. Do not invent new requirements.
- Every FSD functional_spec must reference a requirement ID (FR-XXX) in requirement_ref.
- Every user story must reference a requirement ID (FR-XXX) in requirement_ref.
- Write acceptance criteria in Given/When/Then format.
- BRD risks must have an ID (RISK-001, RISK-002, --ฆ).
- FSD specs must have sequential IDs (FSD-001, FSD-002, --ฆ).
- User stories must have sequential IDs (US-001, US-002, --ฆ).
- You MUST return ONLY a valid JSON object -- no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following documents and produce a BRD, FSD, and User Story Backlog.
Return ONLY the JSON -- no explanation, no code fences.

Schema:
{{
  "brd": {{
    "business_need": "2-4 sentences on why this system is needed",
    "objectives": ["measurable business objective 1"],
    "success_criteria": ["how we will know the project succeeded"],
    "assumptions": ["assumption 1"],
    "constraints": ["constraint 1"],
    "risks": [{{"id": "RISK-001", "description": "risk description", "impact": "High|Medium|Low"}}]
  }},
  "fsd": {{
    "system_overview": "2-4 sentence technical overview of the system",
    "functional_specs": [
      {{
        "id": "FSD-001",
        "requirement_ref": "FR-001",
        "feature": "feature name",
        "description": "detailed functional description",
        "acceptance_criteria": ["Given [context], When [action], Then [result]"]
      }}
    ]
  }},
  "user_stories": [
    {{
      "id": "US-001",
      "requirement_ref": "FR-001",
      "as_a": "role",
      "i_want": "specific goal",
      "so_that": "business benefit",
      "acceptance_criteria": ["Given [context], When [action], Then [result]"],
      "priority": "Must Have|Should Have|Could Have|Won't Have"
    }}
  ]
}}

REQUIREMENT SUMMARY:
{req_summary}

GAP ANALYSIS REPORT:
{gap_report}
"""


# โ"€โ"€ Markdown renderers โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

def _render_brd(data: _BRDOutput, project_id: str, doc_id: str) -> str:
    def _bullets(items: list[str], fallback: str) -> str:
        return "\n".join(f"- {i}" for i in items) if items else f"> {fallback}"

    risk_rows = ""
    if data.risks:
        for r in data.risks:
            risk_rows += f"| {r.id} | {r.description} | {r.impact} |\n"
    else:
        risk_rows = "| -- | No risks identified | -- |\n"

    return f"""\
# Business Requirements Document (BRD)

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** BA Agent v1.0.0
**Pipeline Step:** 3 of 10
**Status:** Draft โ' Awaiting Review

---

## 1. Business Need

{data.business_need or "> Not specified."}

---

## 2. Objectives

{_bullets(data.objectives, "No objectives stated.")}

---

## 3. Success Criteria

{_bullets(data.success_criteria, "No success criteria stated.")}

---

## 4. Assumptions

{_bullets(data.assumptions, "No assumptions stated.")}

---

## 5. Constraints

{_bullets(data.constraints, "No constraints stated.")}

---

## 6. Risks

| ID | Description | Impact |
|---|---|---|
{risk_rows}"""


def _render_fsd(data: _FSDOutput, project_id: str, doc_id: str) -> str:
    specs_section = ""
    for spec in data.functional_specs:
        ac = "\n".join(f"- [ ] {c}" for c in spec.acceptance_criteria) \
            if spec.acceptance_criteria else "> No acceptance criteria."
        ref = f" โ {spec.requirement_ref}" if spec.requirement_ref else ""
        specs_section += f"""
### {spec.id}{ref} -- {spec.feature}

{spec.description}

**Acceptance Criteria:**

{ac}

---
"""

    return f"""\
# Functional Specification Document (FSD)

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** BA Agent v1.0.0
**Pipeline Step:** 3 of 10
**Status:** Draft โ' Awaiting Review

---

## 1. System Overview

{data.system_overview or "> Not specified."}

---

## 2. Functional Specifications
{specs_section if specs_section else "> No functional specifications generated."}"""


def _render_user_stories(stories: list[_UserStory], project_id: str, doc_id: str) -> str:
    stories_section = ""
    for us in stories:
        ac = "\n".join(f"- [ ] {c}" for c in us.acceptance_criteria) \
            if us.acceptance_criteria else "> No acceptance criteria."
        ref = f" โ {us.requirement_ref}" if us.requirement_ref else ""
        stories_section += f"""
## {us.id}{ref} [{us.priority}]

**As a** {us.as_a}, **I want** {us.i_want}, **so that** {us.so_that}.

**Acceptance Criteria:**

{ac}

---
"""

    return f"""\
# User Story Backlog

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** BA Agent v1.0.0
**Pipeline Step:** 3 of 10
**Status:** Draft โ' Awaiting Review
**Total Stories:** {len(stories)}

---
{stories_section if stories_section else "> No user stories generated."}"""


# โ"€โ"€ Agent runner โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

class BAAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: PipelineStep | None = None
        agent_row: Agent | None = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("BAAgent skipped -- run %s already failed", run_id)
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

            req_doc, gap_doc = self._load_source_documents(run_id)

            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    req_summary=req_doc.content_markdown,
                    gap_report=gap_doc.content_markdown,
                ),
                model=agent_row.model_name if agent_row else None,
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = BAAgentOutput.model_validate(parsed)

            brd_id, fsd_id, us_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            pid = str(run.project_id)

            brd_doc = Document(
                id=brd_id,
                project_id=run.project_id,
                document_type=DocumentType.brd,
                title="Business Requirements Document",
                content_markdown=_render_brd(output.brd, pid, str(brd_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            fsd_doc = Document(
                id=fsd_id,
                project_id=run.project_id,
                document_type=DocumentType.fsd,
                title="Functional Specification Document",
                content_markdown=_render_fsd(output.fsd, pid, str(fsd_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            us_doc = Document(
                id=us_id,
                project_id=run.project_id,
                document_type=DocumentType.user_story,
                title="User Story Backlog",
                content_markdown=_render_user_stories(output.user_stories, pid, str(us_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(brd_doc)
            self.session.add(fsd_doc)
            self.session.add(us_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = brd_doc.id  # BRD is the primary output
            step.completed_at = datetime.now(UTC)

            # Gate 2 -- wait for human review of BRD/FSD/User Stories
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            self._log_activity(
                run.project_id, agent_row,
                f"BA documents created: BRD, FSD ({len(output.fsd.functional_specs)} specs), "
                f"User Stories ({len(output.user_stories)}). Awaiting Gate 2 review.",
            )
            self.session.commit()

            from app.agents._workspace import write_workspace_docs
            write_workspace_docs(self.session, run.project_id, {
                "brd.md":          brd_doc.content_markdown,
                "fsd.md":          fsd_doc.content_markdown,
                "user_stories.md": us_doc.content_markdown,
            })
            logger.info(
                "BAAgent completed run=%s brd=%s fsd=%s us=%s",
                run_id, brd_id, fsd_id, us_id,
            )

        except Exception as exc:
            logger.exception("BAAgent failed run=%s: %s", run_id, exc)
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

    # โ"€โ"€ helpers โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

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

    def _get_agent_row(self) -> Agent | None:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_source_documents(self, run_id: uuid.UUID) -> tuple[Document, Document]:
        steps = self.session.exec(
            select(PipelineStep).where(PipelineStep.pipeline_run_id == run_id)
        ).all()

        doc_ids = {s.step_name: s.output_document_id for s in steps if s.output_document_id}

        req_doc_id = doc_ids.get("requirement_summary")
        gap_doc_id = doc_ids.get("gap_analysis")
        if not req_doc_id or not gap_doc_id:
            raise ValueError("requirement_summary or gap_analysis output document missing")

        req_doc = self.session.get(Document, req_doc_id)
        gap_doc = self.session.get(Document, gap_doc_id)
        if not req_doc or not gap_doc:
            raise ValueError("Source documents not found in database")
        return req_doc, gap_doc

    def _log_activity(self, project_id: uuid.UUID, agent_row: Agent | None, message: str) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
