"""Change Impact Agent โ€” Pipeline Step 8.

Triggered manually when a requirement changes after BA/SA work has begun.
Reads all available project documents and produces a Change Impact Report
covering: affected artifacts, effort estimate, risk assessment, and
recommendations on which agents need to be re-run.
"""
import logging
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
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "change-impact-agent"
TIMEOUT_SECONDS = 240.0


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


# โ”€โ”€ Output schemas โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class _AffectedArtifact(BaseModel):
    artifact_type: str
    affected_section: str = ""
    nature: str = "Update"
    effort_days: float = 1.0


class _ImpactItem(BaseModel):
    artifact_id: str = ""
    current_text: str = ""
    required_change: str
    priority: str = "High"


class _ApiImpact(BaseModel):
    api_id: str = ""
    endpoint: str
    change_type: str
    breaking_change: bool = False
    migration_required: bool = False


class _DbImpact(BaseModel):
    db_id: str = ""
    table_column: str
    change_type: str
    migration_required: bool = False


class _ScreenImpact(BaseModel):
    ui_id: str = ""
    screen: str
    affected_component: str
    required_change: str


class _TestImpact(BaseModel):
    tc_id: str = ""
    test_description: str
    action: str = "Update"


class _EffortRow(BaseModel):
    layer: str
    tasks_affected: int = 0
    estimated_days: float = 1.0
    notes: str = ""


class _Risk(BaseModel):
    risk: str
    likelihood: str = "Medium"
    impact: str = "Medium"
    mitigation: str


class ChangeImpactOutput(BaseModel):
    severity: str = "Medium"
    change_summary: str
    affected_artifacts: list[_AffectedArtifact] = Field(default_factory=list)
    fsd_impacts: list[_ImpactItem] = Field(default_factory=list)
    api_impacts: list[_ApiImpact] = Field(default_factory=list)
    database_impacts: list[_DbImpact] = Field(default_factory=list)
    screen_impacts: list[_ScreenImpact] = Field(default_factory=list)
    test_case_impacts: list[_TestImpact] = Field(default_factory=list)
    effort_estimate: list[_EffortRow] = Field(default_factory=list)
    risk_assessment: list[_Risk] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    has_breaking_api_change: bool = False
    has_db_migration: bool = False
    total_effort_days: float = 0.0


# โ”€โ”€ Prompts โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

_SYSTEM_PROMPT = """\
You are the Change Impact Agent in an AI-powered software factory.
When a requirement changes, you analyse every downstream artifact and produce
a precise Change Impact Report โ€” what breaks, what must be updated, effort,
risks, and which agents need to be re-run.

CRITICAL RULES:
- Flag every breaking API change explicitly (breaking_change: true).
- Flag every DB migration requirement explicitly (migration_required: true).
- Effort estimates must be conservative โ€” multiply first estimate by 1.3.
- Recommend re-running agents by name, not just re-writing documents.
- Cite artifact IDs (FSD-XXX, API-XXX, DB-XXX, UI-XXX, TC-XXX) in every impact row.
- If a document was not provided, note it as "Not analysed โ€” document not provided".
- Do NOT modify or rewrite upstream documents โ€” analysis only.
- You MUST return ONLY a valid JSON object โ€” no prose, no markdown wrapping.
"""

_TASK_TEMPLATE = """\
A requirement has changed in this project. Analyse the impact across all
provided downstream documents and return ONLY the JSON โ€” no explanation.

CHANGE DESCRIPTION:
{change_description}

CHANGED REQUIREMENT IDs: {changed_ids}

CONTEXT NOTES: {context_notes}

Schema:
{{
  "severity": "Low|Medium|High|Critical",
  "change_summary": "2-3 sentence summary of what changed and overall impact",
  "affected_artifacts": [
    {{
      "artifact_type": "FSD|API|DB|Screen|Test Case|BRD",
      "affected_section": "FSD-003",
      "nature": "Update|Add|Delete|Breaking Change",
      "effort_days": 1.5
    }}
  ],
  "fsd_impacts": [
    {{
      "artifact_id": "FSD-003",
      "current_text": "brief description of current spec",
      "required_change": "what must change",
      "priority": "Critical|High|Medium|Low"
    }}
  ],
  "api_impacts": [
    {{
      "api_id": "API-005",
      "endpoint": "POST /orders",
      "change_type": "Add field | Remove field | Change response | New endpoint | Deprecate",
      "breaking_change": true,
      "migration_required": false
    }}
  ],
  "database_impacts": [
    {{
      "db_id": "DB-003",
      "table_column": "orders.discount_pct",
      "change_type": "Add column | Drop column | Change type | Add constraint",
      "migration_required": true
    }}
  ],
  "screen_impacts": [
    {{
      "ui_id": "UI-005",
      "screen": "Order Summary Screen",
      "affected_component": "Discount field",
      "required_change": "Add discount percentage display"
    }}
  ],
  "test_case_impacts": [
    {{
      "tc_id": "TC-012",
      "test_description": "Verify order total calculation",
      "action": "Update|Add|Delete"
    }}
  ],
  "effort_estimate": [
    {{
      "layer": "Backend|Frontend|DB Migration|Test Update|Documentation",
      "tasks_affected": 3,
      "estimated_days": 2.0,
      "notes": "Additional context"
    }}
  ],
  "risk_assessment": [
    {{
      "risk": "Risk description",
      "likelihood": "Low|Medium|High",
      "impact": "Low|Medium|High",
      "mitigation": "Mitigation action"
    }}
  ],
  "recommendations": [
    "Re-run BA Agent for FSD-003 and FSD-007 (owner: BA Agent, urgency: Immediate)",
    "Re-run QA Agent to update test cases TC-012 and TC-015 (owner: QA Agent, urgency: Before next sprint)"
  ],
  "has_breaking_api_change": false,
  "has_db_migration": false,
  "total_effort_days": 5.0
}}

REQUIREMENT SUMMARY (current):
{req_summary}

FSD (if available):
{fsd}

API SPECIFICATION (if available):
{api_spec}

DATABASE DESIGN (if available):
{database}

SCREEN SPECIFICATION (if available):
{screen_spec}

TEST CASES (if available):
{test_cases}
"""


# โ”€โ”€ Markdown renderer โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _cell(s: str) -> str:
    """Escape pipe characters so they don't break Markdown table columns."""
    return s.replace("|", "\\|")


def _render_report(
    output: ChangeImpactOutput,
    project_id: str,
    doc_id: str,
    change_description: str,
    changed_ids: list[str],
) -> str:
    severity_badge = {
        "Low": "๐ข Low",
        "Medium": "๐ก Medium",
        "High": "๐  High",
        "Critical": "๐”ด Critical",
    }.get(output.severity, output.severity)

    def _artifact_rows() -> str:
        if not output.affected_artifacts:
            return "| โ€” | โ€” | โ€” | โ€” |\n"
        return "".join(
            f"| {_cell(a.artifact_type)} | {_cell(a.affected_section)} "
            f"| {_cell(a.nature)} | {a.effort_days}d |\n"
            for a in output.affected_artifacts
        )

    def _fsd_rows() -> str:
        if not output.fsd_impacts:
            return ""
        rows = "| FSD ID | Current Text | Required Change | Priority |\n|---|---|---|---|\n"
        rows += "".join(
            f"| {_cell(i.artifact_id)} | {_cell(i.current_text)} "
            f"| {_cell(i.required_change)} | {_cell(i.priority)} |\n"
            for i in output.fsd_impacts
        )
        return f"\n### FSD Impact\n\n{rows}"

    def _api_rows() -> str:
        if not output.api_impacts:
            return ""
        rows = "| API ID | Endpoint | Change Type | Breaking? | Migration? |\n|---|---|---|---|---|\n"
        rows += "".join(
            f"| {_cell(i.api_id)} | `{_cell(i.endpoint)}` | {_cell(i.change_type)} "
            f"| {'Yes' if i.breaking_change else 'No'} "
            f"| {'Yes' if i.migration_required else 'No'} |\n"
            for i in output.api_impacts
        )
        return f"\n### API Impact\n\n{rows}"

    def _db_rows() -> str:
        if not output.database_impacts:
            return ""
        rows = "| DB ID | Table / Column | Change Type | Migration? |\n|---|---|---|---|\n"
        rows += "".join(
            f"| {_cell(i.db_id)} | `{_cell(i.table_column)}` | {_cell(i.change_type)} "
            f"| {'Yes' if i.migration_required else 'No'} |\n"
            for i in output.database_impacts
        )
        return f"\n### Database Impact\n\n{rows}"

    def _screen_rows() -> str:
        if not output.screen_impacts:
            return ""
        rows = "| UI ID | Screen | Affected Component | Required Change |\n|---|---|---|---|\n"
        rows += "".join(
            f"| {_cell(i.ui_id)} | {_cell(i.screen)} "
            f"| {_cell(i.affected_component)} | {_cell(i.required_change)} |\n"
            for i in output.screen_impacts
        )
        return f"\n### Screen Impact\n\n{rows}"

    def _tc_rows() -> str:
        if not output.test_case_impacts:
            return ""
        rows = "| TC ID | Test Description | Action |\n|---|---|---|\n"
        rows += "".join(
            f"| {_cell(i.tc_id)} | {_cell(i.test_description)} | {_cell(i.action)} |\n"
            for i in output.test_case_impacts
        )
        return f"\n### Test Case Impact\n\n{rows}"

    def _effort_rows() -> str:
        if not output.effort_estimate:
            return "| โ€” | โ€” | โ€” | โ€” |\n"
        return "".join(
            f"| {_cell(e.layer)} | {e.tasks_affected} | {e.estimated_days}d | {_cell(e.notes)} |\n"
            for e in output.effort_estimate
        )

    def _risk_rows() -> str:
        if not output.risk_assessment:
            return "| โ€” | โ€” | โ€” | โ€” |\n"
        return "".join(
            f"| {_cell(r.risk)} | {_cell(r.likelihood)} "
            f"| {_cell(r.impact)} | {_cell(r.mitigation)} |\n"
            for r in output.risk_assessment
        )

    recs = "\n".join(f"- {r}" for r in output.recommendations) \
        if output.recommendations else "> No recommendations."

    alerts = []
    if output.has_breaking_api_change:
        alerts.append("> โ ๏ธ **Breaking API Change detected** โ€” clients must be updated.")
    if output.has_db_migration:
        alerts.append("> โ ๏ธ **Database migration required** โ€” migration script must be prepared.")
    alert_block = "\n".join(alerts) + "\n" if alerts else ""

    return f"""\
# Change Impact Report

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Change Impact Agent v1.0.0
**Pipeline Step:** 8 of 10
**Status:** Draft โ’ Awaiting Review

---

## 1. Change Summary

**Changed Requirements:** {", ".join(changed_ids)}
**Severity:** {severity_badge}

{alert_block}
{output.change_summary}

---

## 2. Change Description

{change_description}

---

## 3. Affected Artifacts

| Artifact Type | Affected Section | Nature of Change | Effort |
|---|---|---|---|
{_artifact_rows()}
{_fsd_rows()}{_api_rows()}{_db_rows()}{_screen_rows()}{_tc_rows()}

---

## 4. Effort Estimate

| Layer | Tasks Affected | Estimated Days | Notes |
|---|---|---|---|
{_effort_rows()}

**Total Estimated Effort:** {output.total_effort_days} days

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
{_risk_rows()}

---

## 6. Recommendations

{recs}
"""


# โ”€โ”€ Agent runner โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class ChangeImpactAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(
        self,
        project_id: uuid.UUID,
        change_description: str,
        changed_requirement_ids: list[str],
        context_notes: str = "",
    ) -> Document:
        agent_row = self._get_agent_row()

        if agent_row:
            agent_row.status = AgentStatus.working
            agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

        try:
            docs = self._load_documents(project_id)

            raw_json = _llm.call_ollama(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_TASK_TEMPLATE.format(
                    change_description=_esc(change_description),
                    changed_ids=", ".join(changed_requirement_ids),
                    context_notes=_esc(context_notes) if context_notes else "(none)",
                    req_summary=_esc(docs.get("req_summary", "(not available)")),
                    fsd=_esc(docs.get("fsd", "(not available)")),
                    api_spec=_esc(docs.get("api_spec", "(not available)")),
                    database=_esc(docs.get("database", "(not available)")),
                    screen_spec=_esc(docs.get("screen_spec", "(not available)")),
                    test_cases=_esc(docs.get("test_cases", "(not available)")),
                ),
                model=agent_row.model_name if agent_row else None,
                timeout=TIMEOUT_SECONDS,
            )

            parsed = _llm.extract_json(raw_json)
            output = ChangeImpactOutput.model_validate(parsed)

            # Override computed flags in case LLM didn't set them
            if not output.has_breaking_api_change:
                output.has_breaking_api_change = any(
                    i.breaking_change for i in output.api_impacts
                )
            if not output.has_db_migration:
                output.has_db_migration = any(
                    i.migration_required for i in output.database_impacts
                )
            if not output.total_effort_days:
                output.total_effort_days = sum(
                    e.estimated_days for e in output.effort_estimate
                )

            doc_id = uuid.uuid4()
            pid = str(project_id)

            report_doc = Document(
                id=doc_id,
                project_id=project_id,
                document_type=DocumentType.change_impact_report,
                title=f"Change Impact Report โ€” {', '.join(changed_requirement_ids)}",
                content_markdown=_render_report(
                    output, pid, str(doc_id), change_description, changed_requirement_ids
                ),
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(report_doc)

            self._log_activity(
                project_id, agent_row,
                f"Change impact report created for requirements "
                f"{', '.join(changed_requirement_ids)}. "
                f"Severity: {output.severity}. "
                f"Affected artifacts: {len(output.affected_artifacts)}. "
                f"Total effort: {output.total_effort_days}d. "
                f"Breaking API: {output.has_breaking_api_change}. "
                f"DB migration: {output.has_db_migration}.",
            )

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            self.session.commit()
            self.session.refresh(report_doc)

            from app.agents._workspace import write_workspace_docs

            write_workspace_docs(self.session, project_id, {"change_impact_report.md": report_doc.content_markdown})

            logger.info(
                "ChangeImpactAgent completed project=%s doc=%s severity=%s artifacts=%d",
                project_id, doc_id, output.severity, len(output.affected_artifacts),
            )
            return report_doc

        except Exception as exc:
            logger.exception("ChangeImpactAgent failed project=%s: %s", project_id, exc)
            self.session.rollback()
            if agent_row:
                try:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.now(UTC)
                    self.session.commit()
                except Exception:
                    pass
            raise

    # โ”€โ”€ helpers โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_documents(self, project_id: uuid.UUID) -> dict[str, str]:
        type_key = {
            DocumentType.requirement_summary: "req_summary",
            DocumentType.fsd:                 "fsd",
            DocumentType.api_spec:            "api_spec",
            DocumentType.database_design:     "database",
            DocumentType.screen_spec:         "screen_spec",
            DocumentType.test_report:         "test_cases",
        }
        result: dict[str, str] = {}
        for doc_type, key in type_key.items():
            doc = self.session.exec(
                select(Document).where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                ).order_by(Document.created_at.desc())
            ).first()
            if doc:
                result[key] = doc.content_markdown
        return result

    def _log_activity(
        self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str
    ) -> None:
        self.session.add(ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        ))
