"""QA Agent โ€” Pipeline Step 7.

Reads approved FSD, User Stories, API Spec, and (optionally) Screen Spec to produce:
  - Test Cases document (functional, API, edge-case, negative)
  - UAT Script document (UAT scenarios + sign-off criteria)
"""
import logging
import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
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

AGENT_NAME = "qa-agent"


def _esc(s: str) -> str:
    """Escape braces in document content so str.format() doesn't misinterpret them."""
    return s.replace("{", "{{").replace("}", "}}")
STEP_NAME = “test_cases”
TIMEOUT_SECONDS = 480.0


# โ”€โ”€ Output schemas (all fields optional to tolerate LLM schema drift) โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class _LenientBase(BaseModel):
    model_config = ConfigDict(extra=”ignore”)


class _FunctionalTC(_LenientBase):
    id: str = “TC-001”
    fsd_ref: str = “”
    story_ref: str = “”
    description: str = “”
    precondition: str = “”
    steps: list[str] = Field(default_factory=list)
    expected_result: str = “”
    priority: str = “High”


class _ApiTC(_LenientBase):
    id: str = “TC-010”
    api_ref: str = “”
    method: str = “GET”
    endpoint: str = “”
    request_body: str = “โ€””
    expected_status: int = 200
    expected_response: str = “”
    priority: str = “High”


class _EdgeTC(_LenientBase):
    id: str = “TC-020”
    fsd_ref: str = “”
    scenario: str = “”
    input: str = “”
    expected_behaviour: str = “”


class _NegativeTC(_LenientBase):
    id: str = “TC-030”
    fsd_ref: str = “”
    scenario: str = “”
    invalid_input: str = “”
    expected_error: str = “”


class _UATScenario(_LenientBase):
    id: str = “UAT-001”
    story_ref: str = “”
    description: str = “”
    actor: str = “”
    steps: list[str] = Field(default_factory=list)
    expected_outcome: str = “”


class QAAgentOutput(_LenientBase):
    functional_tests: list[_FunctionalTC] = Field(default_factory=list)
    api_tests: list[_ApiTC] = Field(default_factory=list)
    edge_case_tests: list[_EdgeTC] = Field(default_factory=list)
    negative_tests: list[_NegativeTC] = Field(default_factory=list)
    uat_scenarios: list[_UATScenario] = Field(default_factory=list)
    sign_off_criteria: list[str] = Field(default_factory=list)
    minimum_pass_rate: int = 95


# โ”€โ”€ Prompts โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

_SYSTEM_PROMPT = """\
You are the QA Agent in an AI-powered software factory.
Your job is to read the approved FSD, User Stories, and API Specification,
then produce comprehensive Test Cases and a UAT Script.

CRITICAL RULES:
- Every FSD specification (FSD-XXX) must have at least one functional test case.
- Every API endpoint (API-XXX) must have at least one API test case (happy path + at least one error case).
- Assign TC-XXX IDs GLOBALLY โ€” do not restart numbering per section.
  Functional: TC-001..., API: TC-010+, Edge: TC-020+, Negative: TC-030+.
- UAT scenarios must be written in plain language for non-technical business users โ€” no technical jargon.
- Do NOT write test code โ€” test case descriptions and steps only.
- You MUST return ONLY a valid JSON object โ€” no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
Analyze the following approved documents and produce a comprehensive QA document.
Return ONLY the JSON โ€” no explanation, no code fences.

Schema:
{{
  "functional_tests": [
    {{
      "id": "TC-001",
      "fsd_ref": "FSD-001",
      "story_ref": "US-001",
      "description": "one-sentence test description",
      "precondition": "what must be true before the test",
      "steps": ["Step 1: ...", "Step 2: ..."],
      "expected_result": "exact observable outcome",
      "priority": "Critical|High|Medium|Low"
    }}
  ],
  "api_tests": [
    {{
      "id": "TC-010",
      "api_ref": "API-001",
      "method": "POST",
      "endpoint": "/projects",
      "request_body": "{{\"name\": \"Test\"}}",
      "expected_status": 201,
      "expected_response": "id, name, status fields present",
      "priority": "Critical|High|Medium|Low"
    }}
  ],
  "edge_case_tests": [
    {{
      "id": "TC-020",
      "fsd_ref": "FSD-001",
      "scenario": "boundary condition description",
      "input": "input at boundary",
      "expected_behaviour": "expected result"
    }}
  ],
  "negative_tests": [
    {{
      "id": "TC-030",
      "fsd_ref": "FSD-001",
      "scenario": "missing required field X",
      "invalid_input": "request without field X",
      "expected_error": "422 VALIDATION_ERROR โ€” field required"
    }}
  ],
  "uat_scenarios": [
    {{
      "id": "UAT-001",
      "story_ref": "US-001",
      "description": "plain-language scenario description",
      "actor": "business role performing the test",
      "steps": ["Go to ...", "Click ...", "Verify ..."],
      "expected_outcome": "what the user should see"
    }}
  ],
  "sign_off_criteria": [
    "TC-001 (critical path login) must pass",
    "All Critical priority test cases must pass"
  ],
  "minimum_pass_rate": 95
}}

FUNCTIONAL SPECIFICATION DOCUMENT (FSD):
{fsd}

USER STORIES:
{user_story}

API SPECIFICATION:
{api_spec}

SCREEN SPECIFICATION:
{screen_spec}
"""


# โ”€โ”€ Markdown renderers โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _render_test_cases(data: QAAgentOutput, project_id: str, doc_id: str,
                       fsd_id: str, story_id: str, api_id: str) -> str:
    def _func_rows(tests: list[_FunctionalTC]) -> str:
        if not tests:
            return "| โ€” | โ€” | โ€” | โ€” | โ€” | โ€” | โ€” | โ€” |\n"
        rows = ""
        for t in tests:
            steps = " ".join(f"{i+1}. {s}" for i, s in enumerate(t.steps)) or "โ€”"
            rows += (
                f"| {t.id} | {t.fsd_ref} | {t.story_ref} | {t.description} "
                f"| {t.precondition} | {steps} | {t.expected_result} | {t.priority} |\n"
            )
        return rows

    def _api_rows(tests: list[_ApiTC]) -> str:
        if not tests:
            return "| โ€” | โ€” | โ€” | โ€” | โ€” | โ€” | โ€” | โ€” |\n"
        rows = ""
        for t in tests:
            rows += (
                f"| {t.id} | {t.api_ref} | {t.method} | `{t.endpoint}` "
                f"| `{t.request_body}` | {t.expected_status} | {t.expected_response} | {t.priority} |\n"
            )
        return rows

    def _edge_rows(tests: list[_EdgeTC]) -> str:
        if not tests:
            return "| โ€” | โ€” | โ€” | โ€” | โ€” |\n"
        return "".join(
            f"| {t.id} | {t.fsd_ref} | {t.scenario} | {t.input} | {t.expected_behaviour} |\n"
            for t in tests
        )

    def _neg_rows(tests: list[_NegativeTC]) -> str:
        if not tests:
            return "| โ€” | โ€” | โ€” | โ€” | โ€” |\n"
        return "".join(
            f"| {t.id} | {t.fsd_ref} | {t.scenario} | {t.invalid_input} | {t.expected_error} |\n"
            for t in tests
        )

    total = (len(data.functional_tests) + len(data.api_tests)
             + len(data.edge_case_tests) + len(data.negative_tests))

    return f"""\
# Test Cases

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** QA Agent v1.0.0
**Pipeline Step:** 7 of 10
**Source Documents:** FSD `{fsd_id}`, User Stories `{story_id}`, API Spec `{api_id}`
**Status:** Draft โ’ Awaiting Review

---

## 1. Test Summary

| Type | Count |
|---|---|
| Functional Tests | {len(data.functional_tests)} |
| API Tests | {len(data.api_tests)} |
| Edge Case Tests | {len(data.edge_case_tests)} |
| Negative Tests | {len(data.negative_tests)} |
| **Total** | **{total}** |

---

## 2. Functional Test Cases

| TC ID | FSD Ref | Story Ref | Test Description | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|---|
{_func_rows(data.functional_tests)}

---

## 3. API Test Cases

| TC ID | API Ref | Method | Endpoint | Request Body | Expected Status | Expected Response | Priority |
|---|---|---|---|---|---|---|---|
{_api_rows(data.api_tests)}

---

## 4. Edge Case Tests

| TC ID | FSD Ref | Scenario | Input | Expected Behaviour |
|---|---|---|---|---|
{_edge_rows(data.edge_case_tests)}

---

## 5. Negative Tests

| TC ID | FSD Ref | Scenario | Invalid Input | Expected Error |
|---|---|---|---|---|
{_neg_rows(data.negative_tests)}
"""


def _render_uat_script(data: QAAgentOutput, project_id: str, doc_id: str) -> str:
    def _uat_rows(scenarios: list[_UATScenario]) -> str:
        if not scenarios:
            return "| โ€” | โ€” | โ€” | โ€” | โ€” | โ€” | โ€” |\n"
        rows = ""
        for s in scenarios:
            steps = " ".join(f"{i+1}. {st}" for i, st in enumerate(s.steps)) or "โ€”"
            rows += (
                f"| {s.id} | {s.story_ref} | {s.description} | {s.actor} "
                f"| {steps} | {s.expected_outcome} | โ Pass / โ Fail |\n"
            )
        return rows

    criteria = "\n".join(f"- {c}" for c in data.sign_off_criteria) \
        if data.sign_off_criteria else "> No sign-off criteria defined."

    return f"""\
# UAT Script

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** QA Agent v1.0.0
**Pipeline Step:** 7 of 10
**Status:** Draft โ’ Awaiting Review

---

## 1. UAT Overview

**Objective:** Verify that all user-facing features work correctly and meet business requirements.
**Scope:** All features described in the approved User Stories.
**Target Users:** Business stakeholders and product owners.
**Minimum Pass Rate for Sign-Off:** {data.minimum_pass_rate}%

---

## 2. UAT Scenarios

| Scenario ID | Story Ref | Scenario Description | Actor | Steps | Expected Outcome | Pass / Fail |
|---|---|---|---|---|---|---|
{_uat_rows(data.uat_scenarios)}

---

## 3. Sign-Off Criteria

{criteria}

---

## 4. Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Product Owner | | | |
| Business Analyst | | | |
| QA Lead | | | |
"""


# โ”€โ”€ Agent runner โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class QAAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("QAAgent skipped โ€” run %s already failed", run_id)
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

            fsd_doc, story_doc, api_doc, screen_doc = \
                self._load_source_documents(run.project_id)

            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    fsd=_esc(fsd_doc.content_markdown),
                    user_story=_esc(story_doc.content_markdown),
                    api_spec=_esc(api_doc.content_markdown),
                    screen_spec=_esc(screen_doc.content_markdown) if screen_doc else "(not available)",
                ),
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = QAAgentOutput.model_validate(parsed)

            pid = str(run.project_id)
            fsd_id = str(fsd_doc.id)
            story_id = str(story_doc.id)
            api_id = str(api_doc.id)

            # Save Test Cases document
            tc_doc_id = uuid.uuid4()
            tc_doc = Document(
                id=tc_doc_id,
                project_id=run.project_id,
                document_type=DocumentType.test_cases,
                title="Test Cases",
                content_markdown=_render_test_cases(
                    output, pid, str(tc_doc_id), fsd_id, story_id, api_id
                ),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(tc_doc)

            # Save UAT Script document
            uat_doc_id = uuid.uuid4()
            uat_doc = Document(
                id=uat_doc_id,
                project_id=run.project_id,
                document_type=DocumentType.uat_script,
                title="UAT Script",
                content_markdown=_render_uat_script(output, pid, str(uat_doc_id)),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(uat_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = tc_doc.id
            step.completed_at = datetime.now(UTC)

            # Gate 6 โ€” wait for human review before proceeding
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            total_tc = (len(output.functional_tests) + len(output.api_tests)
                        + len(output.edge_case_tests) + len(output.negative_tests))
            self._log_activity(
                run.project_id, agent_row,
                f"QA documents created: {total_tc} test cases "
                f"({len(output.functional_tests)} functional, {len(output.api_tests)} API, "
                f"{len(output.edge_case_tests)} edge, {len(output.negative_tests)} negative), "
                f"{len(output.uat_scenarios)} UAT scenarios. Awaiting Gate 6 review.",
            )
            self.session.commit()
            logger.info(
                "QAAgent completed run=%s tc_doc=%s uat_doc=%s total_tc=%d uat=%d",
                run_id, tc_doc_id, uat_doc_id, total_tc, len(output.uat_scenarios),
            )

        except Exception as exc:
            logger.exception("QAAgent failed run=%s: %s", run_id, exc)
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

    def _load_source_documents(
        self, project_id: uuid.UUID
    ) -> tuple[Document, Document, Document, Optional[Document]]:
        def _latest(doc_type: DocumentType) -> Optional[Document]:
            return self.session.exec(
                select(Document).where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                ).order_by(Document.created_at.desc())
            ).first()

        fsd = _latest(DocumentType.fsd)
        story = _latest(DocumentType.user_story)
        api = _latest(DocumentType.api_spec)
        screen = _latest(DocumentType.screen_spec)

        missing = [
            name for name, doc in [("FSD", fsd), ("User Stories", story), ("API Spec", api)]
            if not doc
        ]
        if missing:
            raise ValueError(f"Missing source documents: {', '.join(missing)}")

        return fsd, story, api, screen  # type: ignore[return-value]

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        log = ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        )
        self.session.add(log)
