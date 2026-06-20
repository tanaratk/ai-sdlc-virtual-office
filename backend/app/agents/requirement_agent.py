"""Requirement Agent โ€” Pipeline Step 1.

Runtime pattern:
  load inputs โ’ build prompt โ’ call LLM โ’ validate JSON โ’ render Markdown
  โ’ save Document โ’ update PipelineRun/Step/Agent
"""
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

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
    RequirementInput,
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "requirement-agent"


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|")
STEP_NAME = "requirement_summary"
TIMEOUT_SECONDS = 120.0

# โ”€โ”€ Output schema (Pydantic validation) โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _first(data: dict, *keys: str, fallback: str = "") -> str:
    for k in keys:
        if k in data and data[k]:
            return str(data[k])
    return fallback


class _FR(BaseModel):
    id: str = "FR-001"
    requirement: str = ""
    source: str = "input"
    priority: str = "Medium"

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict) and not v.get("requirement"):
            v["requirement"] = _first(v, "description", "text", "content", "detail", "requirements", fallback="(no text)")
        return v


class _NFR(BaseModel):
    id: str = "NFR-001"
    requirement: str = ""
    category: str = "Other"
    priority: str = "Medium"

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict) and not v.get("requirement"):
            v["requirement"] = _first(v, "description", "text", "content", "detail", "requirements", fallback="(no text)")
        return v


class _Stakeholder(BaseModel):
    role: str = ""
    responsibility: str = ""
    involvement: str = "Informed"


class _BR(BaseModel):
    id: str = "BR-001"
    rule: str = ""

    @model_validator(mode="before")
    @classmethod
    def _remap(cls, v: dict) -> dict:
        if isinstance(v, dict) and not v.get("rule"):
            v["rule"] = _first(v, "description", "text", "content", fallback="(no text)")
        return v


class RequirementSummaryOutput(BaseModel):
    business_objective: str = ""
    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    functional_requirements: list[_FR] = Field(default_factory=list)
    non_functional_requirements: list[_NFR] = Field(default_factory=list)
    stakeholders: list[_Stakeholder] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    business_rules: list[_BR] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


# โ”€โ”€ System prompt โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

_SYSTEM_PROMPT = """\
You are the Requirement Agent in an AI-powered software factory.
Your job is to read raw requirement inputs (meeting transcripts, chat logs, documents, \
or manual text) and extract structured requirements.

Rules:
- Never invent information. If something is unclear, flag it as a question.
- Be specific. "System should handle users" is NOT acceptable.
- Do not merge separate requirements.
- Preserve original intent.
- Use professional English.
- You MUST return ONLY a valid JSON object โ€” no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following requirement input(s) and return a JSON object with exactly this schema.
Return ONLY the JSON โ€” no explanation, no code fences.

Schema:
{{
  "business_objective": "2-4 sentences on WHY this system is needed",
  "in_scope": ["feature or process 1", "..."],
  "out_of_scope": ["exclusion 1"],
  "functional_requirements": [
    {{"id": "FR-001", "requirement": "specific behaviour", "source": "input type", "priority": "Critical|High|Medium|Low"}}
  ],
  "non_functional_requirements": [
    {{"id": "NFR-001", "requirement": "specific NFR", "category": "Performance|Security|Availability|Scalability|Usability|Compliance|Other", "priority": "High|Medium|Low"}}
  ],
  "stakeholders": [
    {{"role": "role name", "responsibility": "what they do", "involvement": "Approver|User|Reviewer|Informed|Owner"}}
  ],
  "assumptions": ["assumption 1"],
  "constraints": ["constraint 1"],
  "business_rules": [
    {{"id": "BR-001", "rule": "explicit policy or logic"}}
  ],
  "open_questions": ["specific question needing clarification before design can proceed"]
}}

REQUIREMENT INPUTS:
{content}
"""


# โ”€โ”€ Markdown renderer โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _render_markdown(
    data: RequirementSummaryOutput,
    project_id: str,
    document_id: str,
    input_titles: list[str],
) -> str:
    def _bullets(items: list[str], fallback: str) -> str:
        if not items:
            return f"> {fallback}"
        return "\n".join(f"- {item}" for item in items)

    def _numbered(items: list[str], fallback: str) -> str:
        if not items:
            return f"> {fallback}"
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    fr_table = "| ID | Requirement | Source | Priority |\n|---|---|---|---|\n"
    if data.functional_requirements:
        for fr in data.functional_requirements:
            fr_table += f"| {_cell(fr.id)} | {_cell(fr.requirement)} | {_cell(fr.source)} | {_cell(fr.priority)} |\n"
    else:
        fr_table = "> No functional requirements found in source."

    nfr_table = "| ID | Requirement | Category | Priority |\n|---|---|---|---|\n"
    if data.non_functional_requirements:
        for nfr in data.non_functional_requirements:
            nfr_table += f"| {_cell(nfr.id)} | {_cell(nfr.requirement)} | {_cell(nfr.category)} | {_cell(nfr.priority)} |\n"
    else:
        nfr_table = "> No NFRs stated. Recommend defining SLA, security, and access control requirements."

    sh_table = "| Role | Responsibility | Involvement |\n|---|---|---|\n"
    if data.stakeholders:
        for sh in data.stakeholders:
            sh_table += f"| {_cell(sh.role)} | {_cell(sh.responsibility)} | {_cell(sh.involvement)} |\n"
    else:
        sh_table = "> No stakeholders explicitly mentioned. Recommend confirming with project sponsor."

    br_section = ""
    if data.business_rules:
        br_section = "\n".join(f"**{br.id}:** {br.rule}" for br in data.business_rules)
    else:
        br_section = "> No business rules explicitly stated in source."

    source_titles = ", ".join(input_titles) if input_titles else "N/A"

    return f"""\
# Requirement Summary

**Project ID:** `{project_id}`
**Document ID:** `{document_id}`
**Source(s):** {source_titles}
**Generated By:** Requirement Agent v1.0.0
**Pipeline Step:** 1 of 10
**Status:** Draft

---

## 1. Business Objective

{data.business_objective or "> No information found in source. Need clarification."}

---

## 2. Scope

### In Scope

{_bullets(data.in_scope, "Not explicitly stated. Recommend clarifying with stakeholders.")}

### Out of Scope

{_bullets(data.out_of_scope, "Not explicitly stated. Recommend clarifying with stakeholders.")}

---

## 3. Functional Requirements

{fr_table}

---

## 4. Non-Functional Requirements

{nfr_table}

---

## 5. Stakeholders

{sh_table}

---

## 6. Assumptions

{_numbered(data.assumptions, "No assumptions required to produce this summary.")}

---

## 7. Constraints

{_numbered(data.constraints, "No constraints stated. Recommend asking about timeline, budget, and technology.")}

---

## 8. Business Rules

{br_section}

---

## 9. Open Questions

{_numbered(data.open_questions, "No open questions. All requirements appear complete.")}
"""


# โ”€โ”€ Agent runner โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class RequirementAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: PipelineStep | None = None
        agent_row: Agent | None = None

        try:
            run = self._get_run(run_id)
            step = self._get_step(run_id)
            agent_row = self._get_agent_row()
            inputs = self._load_inputs(run.project_id)

            self._set_status(run, step, agent_row, PipelineRunStatus.running, PipelineStepStatus.running, AgentStatus.working)

            content = self._combine_inputs(inputs)
            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(content=content),
                model=agent_row.model_name if agent_row else None,
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = RequirementSummaryOutput.model_validate(parsed)

            doc_id = uuid.uuid4()
            input_titles = [inp.title or inp.input_type.value for inp in inputs]
            markdown = _render_markdown(output, str(run.project_id), str(doc_id), input_titles)

            doc = Document(
                id=doc_id,
                project_id=run.project_id,
                document_type=DocumentType.requirement_summary,
                title="Requirement Summary",
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

            # Create next step โ€” Gap Analysis Agent will pick it up
            gap_step = PipelineStep(
                pipeline_run_id=run.id,
                step_name="gap_analysis",
                status=PipelineStepStatus.pending,
            )
            self.session.add(gap_step)

            # Run continues โ€” do not complete yet
            run.current_step = None

            if agent_row:
                agent_row.status = AgentStatus.idle
                agent_row.updated_at = datetime.now(UTC)

            self._log_activity(run.project_id, agent_row, f"Requirement summary created. FRs: {len(output.functional_requirements)}, Open questions: {len(output.open_questions)}. Proceeding to gap analysis.")
            self.session.commit()

            from app.agents._workspace import write_workspace_docs
            write_workspace_docs(self.session, run.project_id, {"requirements.md": markdown})
            logger.info("RequirementAgent completed run=%s doc=%s", run_id, doc_id)

        except Exception as exc:
            logger.exception("RequirementAgent failed run=%s: %s", run_id, exc)
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

    def _get_agent_row(self) -> Agent | None:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_inputs(self, project_id: uuid.UUID) -> list[RequirementInput]:
        inputs = self.session.exec(
            select(RequirementInput).where(RequirementInput.project_id == project_id)
        ).all()
        if not inputs:
            raise ValueError("No requirement inputs found. Upload at least one requirement before running the pipeline.")
        return list(inputs)

    def _combine_inputs(self, inputs: list[RequirementInput]) -> str:
        parts = []
        for inp in inputs:
            header = f"[{inp.input_type.value.upper()}]"
            if inp.title:
                header += f" {inp.title}"
            parts.append(f"{header}\n{inp.content}")
        return "\n\n---\n\n".join(parts)

    def _set_status(
        self,
        run: PipelineRun,
        step: PipelineStep,
        agent_row: Agent | None,
        run_status: PipelineRunStatus,
        step_status: PipelineStepStatus,
        agent_status: AgentStatus,
    ) -> None:
        run.status = run_status
        run.current_step = STEP_NAME
        run.started_at = run.started_at or datetime.now(UTC)
        step.status = step_status
        step.started_at = step.started_at or datetime.now(UTC)
        if agent_row:
            agent_row.status = agent_status
            agent_row.updated_at = datetime.now(UTC)
        self.session.commit()

    def _log_activity(self, project_id: uuid.UUID, agent_row: Agent | None, message: str) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
