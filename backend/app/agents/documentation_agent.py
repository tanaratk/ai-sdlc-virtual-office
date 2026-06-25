"""Documentation Agent — Pipeline Step 9.

Collects all available project documents, asks the LLM to write a brief
executive summary, then assembles the full Compiled Document Set in one
Markdown bundle with a cover page, TOC, document index, and all content.

No new content is invented — this agent compiles what already exists.
"""
import logging
import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel
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

AGENT_NAME = "documentation-agent"
TIMEOUT_SECONDS = 120.0

# Pipeline order for compilation
_DOC_ORDER: list[tuple[DocumentType, str]] = [
    (DocumentType.requirement_summary,  "Requirement Summary"),
    (DocumentType.gap_analysis_report,  "Gap Analysis Report"),
    (DocumentType.brd,                  "Business Requirements Document (BRD)"),
    (DocumentType.fsd,                  "Functional Specification Document (FSD)"),
    (DocumentType.user_story,           "User Stories"),
    (DocumentType.architecture_design,  "Architecture Design"),
    (DocumentType.database_design,      "Database Design"),
    (DocumentType.api_spec,             "API Specification"),
    (DocumentType.screen_spec,          "Screen Specification"),
    (DocumentType.code_task_list,       "Code Task List"),
    (DocumentType.test_cases,           "Test Cases"),
    (DocumentType.test_report,          "Test Report"),
    (DocumentType.devops_config,        "DevOps Configuration"),
    (DocumentType.build_report,         "Build Report"),
    (DocumentType.monitoring_report,    "Monitoring Report"),
    (DocumentType.uat_script,           "UAT Script"),
    (DocumentType.change_impact_report, "Change Impact Report"),
]

_SYSTEM_PROMPT = """\
You are the Documentation Agent in an AI-powered software factory.
Your only task right now is to write a concise executive summary (3–5 sentences)
for the project, based on the requirement summary provided.

RULES:
- Do NOT invent requirements or design decisions not mentioned in the input.
- Write in plain English — no jargon, no bullet lists, no headings.
- Return ONLY a JSON object with one key: "executive_summary".
- Example: {"executive_summary": "This project aims to ..."}
"""

_TASK_TEMPLATE = """\
Write a 3–5 sentence executive summary for this software project.

PROJECT NAME: {project_name}
DOCUMENTS COMPILED: {doc_count}

REQUIREMENT SUMMARY:
{req_summary}

Return ONLY: {{"executive_summary": "..."}}
"""


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


class DocumentationAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, project_id: uuid.UUID, project_name: str) -> Document:
        agent_row = self._get_agent_row()

        if agent_row:
            agent_row.status = AgentStatus.working
            agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

        try:
            docs = self._load_documents(project_id)

            if not docs:
                raise ValueError("No documents found for this project. Run pipeline agents first.")

            exec_summary = self._generate_executive_summary(
                project_name, docs,
                model=agent_row.model_name if agent_row else None,
            )

            doc_id = uuid.uuid4()
            content = self._render_compiled_doc(
                project_id=str(project_id),
                doc_id=str(doc_id),
                project_name=project_name,
                docs=docs,
                executive_summary=exec_summary,
            )

            compiled = Document(
                id=doc_id,
                project_id=project_id,
                document_type=DocumentType.compiled_documents,
                title=f"Compiled Document Set — {project_name}",
                content_markdown=content,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(compiled)

            self.session.add(ActivityLog(
                project_id=project_id,
                agent_id=agent_row.id if agent_row else None,
                event_type=EventType.document_created,
                message=(
                    f"Compiled Document Set created for project '{project_name}'. "
                    f"{len(docs)} document(s) bundled."
                ),
            ))

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            self.session.commit()
            self.session.refresh(compiled)

            logger.info(
                "DocumentationAgent completed project=%s doc=%s sections=%d",
                project_id, doc_id, len(docs),
            )
            return compiled

        except Exception as exc:
            logger.exception("DocumentationAgent failed project=%s: %s", project_id, exc)
            self.session.rollback()
            if agent_row:
                try:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.now(UTC)
                    self.session.commit()
                except Exception:
                    pass
            raise

    # ── helpers ────────────────────────────────────────────────────────────────

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _load_documents(self, project_id: uuid.UUID) -> list[tuple[str, Document]]:
        """Return (label, doc) pairs in pipeline order, skipping missing types."""
        result = []
        for doc_type, label in _DOC_ORDER:
            doc = self.session.exec(
                select(Document).where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                ).order_by(Document.created_at.desc())
            ).first()
            if doc:
                result.append((label, doc))
        return result

    def _generate_executive_summary(
        self, project_name: str, docs: list[tuple[str, Document]],
        model: str | None = None,
    ) -> str:
        req_summary = ""
        for label, doc in docs:
            if doc.document_type == DocumentType.requirement_summary:
                req_summary = doc.content_markdown[:3000]
                break

        if not req_summary:
            return (
                f"This document package compiles all AI-generated artifacts "
                f"for the project '{project_name}'. "
                f"It covers requirements, design, implementation, and test outputs "
                f"produced by the AI-SDLC pipeline."
            )

        raw = _llm.call_ollama(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=_TASK_TEMPLATE.format(
                project_name=_esc(project_name),
                doc_count=len(docs),
                req_summary=_esc(req_summary),
            ),
            model=model,
            timeout=TIMEOUT_SECONDS,
        )
        parsed = _llm.extract_json(raw)

        class _SummaryOut(BaseModel):
            executive_summary: str = ""

        out = _SummaryOut.model_validate(parsed)
        return out.executive_summary or (
            f"This document package compiles all AI-generated artifacts for '{project_name}'."
        )

    def _render_compiled_doc(
        self,
        project_id: str,
        doc_id: str,
        project_name: str,
        docs: list[tuple[str, Document]],
        executive_summary: str,
    ) -> str:
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

        # ── Document index table ──────────────────────────────────────────────
        index_rows = "".join(
            f"| {label} | {doc.title} | {doc.status} | `{doc.id}` |\n"
            for label, doc in docs
        )

        # ── TOC entries ───────────────────────────────────────────────────────
        toc_lines = "\n".join(
            f"{i + 1}. {label}"
            for i, (label, _) in enumerate(docs)
        )

        # ── Document bodies ───────────────────────────────────────────────────
        bodies: list[str] = []
        for i, (label, doc) in enumerate(docs, start=1):
            bodies.append(
                f"---\n\n"
                f"## Section {i}: {label}\n\n"
                f"**Document ID:** `{doc.id}`  \n"
                f"**Type:** {doc.document_type}  \n"
                f"**Status:** {doc.status}  \n"
                f"**Version:** {doc.version}\n\n"
                f"{doc.content_markdown}\n"
            )

        body_block = "\n".join(bodies)

        return f"""\
# Compiled Document Set

**Project:** {project_name}
**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Documentation Agent v1.0.0
**Pipeline Step:** 9 of 10
**Compiled At:** {now}
**Status:** Draft — Awaiting Review

---

## Table of Contents

{toc_lines}

---

## Executive Summary

{executive_summary}

---

## Document Index

| Document Type | Title | Status | Document ID |
|---|---|---|---|
{index_rows}

---

{body_block}
"""
