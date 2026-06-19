"""UX Agent โ€” Pipeline Step 5.

Reads the approved BRD, FSD, and User Story Backlog and produces:
  - Screen Specification (screen list, field spec, user flows, wireframe notes)
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
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "ux-agent"
STEP_NAME = "ux_documents"
TIMEOUT_SECONDS = 180.0


# โ”€โ”€ Output schema โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _first(data: dict, *keys: str, fallback: str = "") -> str:
    for k in keys:
        if k in data and data[k]:
            return str(data[k])
    return fallback


class _Field(BaseModel):
    name: str = ""
    type: str = "text"
    required: bool = True
    validation: str = ""
    description: str = ""

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("name"):
                v["name"] = _first(v, "field_name", "label", "title", fallback="field")
            if not v.get("description"):
                v["description"] = _first(v, "detail", "purpose", "note", fallback="")
        return v


class _Screen(BaseModel):
    id: str = "UI-001"
    name: str = ""
    description: str = ""
    user_role: str = ""
    requirement_refs: list[str] = Field(default_factory=list)
    fields: list[_Field] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    navigation: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("name"):
                v["name"] = _first(v, "screen_name", "title", "label", fallback="Screen")
            if not v.get("description"):
                v["description"] = _first(v, "detail", "purpose", "summary", "overview", fallback="")
            if not v.get("user_role"):
                v["user_role"] = _first(v, "role", "actor", "persona", fallback="")
        return v


class _UserFlow(BaseModel):
    id: str = "FLOW-001"
    name: str = ""
    steps: list[str] = Field(default_factory=list)
    requirement_ref: str = ""

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict):
            if not v.get("name"):
                v["name"] = _first(v, "flow_name", "title", "label", fallback="Flow")
            if not v.get("requirement_ref"):
                v["requirement_ref"] = _first(v, "requirement_refs", "ref", fallback="")
        return v


class UXAgentOutput(BaseModel):
    screens: list[_Screen] = Field(default_factory=list)
    user_flows: list[_UserFlow] = Field(default_factory=list)


# โ”€โ”€ Prompts โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

_SYSTEM_PROMPT = """\
You are the UX Agent in an AI-powered software factory.
Your job is to read the BRD, FSD, and User Story Backlog and produce:
  1. A screen list with field specification for each screen
  2. User interaction flows (user journeys)

Rules:
- Every screen must have a unique ID (UI-001, UI-002, โ€ฆ).
- Every screen must reference a requirement ID (FR-XXX) in requirement_refs.
- Every field must have a type: text, number, date, dropdown, checkbox, textarea, file, password.
- Every user flow must have a unique ID (FLOW-001, FLOW-002, โ€ฆ).
- Write flow steps as clear imperative sentences (e.g., "User clicks Submit button").
- You MUST return ONLY a valid JSON object โ€” no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following BA documents and produce a Screen Specification
with a complete field list and user interaction flows.
Return ONLY the JSON โ€” no explanation, no code fences.

Schema:
{{
  "screens": [
    {{
      "id": "UI-001",
      "name": "Screen Name",
      "description": "what the user does on this screen",
      "user_role": "role who uses this screen (e.g. employee, manager)",
      "requirement_refs": ["FR-001"],
      "fields": [
        {{
          "name": "field_name",
          "type": "text|number|date|dropdown|checkbox|textarea|file|password",
          "required": true,
          "validation": "validation rule or empty string",
          "description": "what this field captures"
        }}
      ],
      "actions": ["Primary action button label", "Secondary action"],
      "navigation": ["Screen name the user can navigate to from here"]
    }}
  ],
  "user_flows": [
    {{
      "id": "FLOW-001",
      "name": "flow name (e.g. Submit Expense Flow)",
      "steps": [
        "1. User navigates to Expense Submission screen",
        "2. User fills in amount and description",
        "3. User clicks Submit",
        "4. System saves the expense and shows confirmation"
      ],
      "requirement_ref": "FR-001"
    }}
  ]
}}

BUSINESS REQUIREMENTS DOCUMENT (BRD):
{brd}

FUNCTIONAL SPECIFICATION DOCUMENT (FSD):
{fsd}

USER STORY BACKLOG:
{user_stories}
"""


# โ”€โ”€ Markdown renderer โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _render_screen_spec(data: UXAgentOutput, project_id: str, doc_id: str) -> str:
    # Screen list summary table
    screen_rows = ""
    for s in data.screens:
        refs = ", ".join(s.requirement_refs) if s.requirement_refs else "โ€”"
        screen_rows += f"| {s.id} | {s.name} | {s.user_role or 'โ€”'} | {refs} |\n"
    if not screen_rows:
        screen_rows = "| โ€” | No screens defined | โ€” | โ€” |\n"

    # Detailed screen specs
    screens_detail = ""
    for s in data.screens:
        refs = ", ".join(s.requirement_refs) if s.requirement_refs else "โ€”"

        field_rows = ""
        for f in s.fields:
            req_str = "Yes" if f.required else "No"
            val = f.validation if f.validation else "โ€”"
            field_rows += f"| `{f.name}` | {f.type} | {req_str} | {val} | {f.description} |\n"

        actions_str = "\n".join(f"- `{a}`" for a in s.actions) if s.actions else "> No actions defined."
        nav_str = "\n".join(f"- {n}" for n in s.navigation) if s.navigation else "> No navigation defined."
        _fld_hdr = "| Field | Type | Required | Validation | Description |\n|---|---|---|---|---|\n"
        _fld_block = (_fld_hdr + field_rows) if field_rows else "> No input fields on this screen."

        screens_detail += f"""
### {s.id} โ€” {s.name}

**User Role:** {s.user_role or "โ€”"}
**Requirement Refs:** {refs}

{s.description}

**Fields:**

{_fld_block}

**Actions:**

{actions_str}

**Navigation:**

{nav_str}

---
"""

    # User flows
    flows_detail = ""
    for flow in data.user_flows:
        ref = f" โ {flow.requirement_ref}" if flow.requirement_ref else ""
        steps_str = "\n".join(f"{step}" for step in flow.steps) if flow.steps \
            else "> No steps defined."
        flows_detail += f"""
### {flow.id}{ref} โ€” {flow.name}

{steps_str}

---
"""

    return f"""\
# Screen Specification

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** UX Agent v1.0.0
**Pipeline Step:** 5 of 10
**Status:** Draft โ’ Awaiting Review
**Total Screens:** {len(data.screens)}
**Total User Flows:** {len(data.user_flows)}

---

## 1. Screen Inventory

| ID | Screen Name | User Role | Requirement Refs |
|---|---|---|---|
{screen_rows}

---

## 2. Screen Specifications
{screens_detail if screens_detail else "> No screens defined."}

## 3. User Interaction Flows
{flows_detail if flows_detail else "> No user flows defined."}"""


# โ”€โ”€ Agent runner โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class UXAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("UXAgent skipped โ€” run %s already failed", run_id)
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

            brd_doc, fsd_doc, us_doc = self._load_ba_documents(run.project_id)

            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    brd=brd_doc.content_markdown,
                    fsd=fsd_doc.content_markdown,
                    user_stories=us_doc.content_markdown,
                ),
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = UXAgentOutput.model_validate(parsed)

            screen_id = uuid.uuid4()
            pid = str(run.project_id)

            screen_doc = Document(
                id=screen_id,
                project_id=run.project_id,
                document_type=DocumentType.screen_spec,
                title="Screen Specification",
                content_markdown=_render_screen_spec(output, pid, str(screen_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(screen_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = screen_doc.id
            step.completed_at = datetime.now(UTC)

            # Gate 4 โ€” wait for human review of Screen Specification
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            self._log_activity(
                run.project_id, agent_row,
                f"Screen spec created: {len(output.screens)} screens, "
                f"{len(output.user_flows)} user flows. Awaiting Gate 4 review.",
            )
            self.session.commit()
            logger.info(
                "UXAgent completed run=%s screen_doc=%s screens=%d flows=%d",
                run_id, screen_id, len(output.screens), len(output.user_flows),
            )

        except Exception as exc:
            logger.exception("UXAgent failed run=%s: %s", run_id, exc)
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

    # โ”€โ”€ helpers โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

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
