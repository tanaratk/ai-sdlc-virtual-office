"""Add skill_markdown column to agents table and seed default skill docs

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SKILLS: dict[str, str] = {
    "requirement-agent": """\
# Requirement Agent — Skill Document

## Role
Parses raw requirement inputs (text, transcript, document) and produces a structured
Requirement Summary that all downstream agents depend on.

## Layer
Business Layer — Step 1 of 12

## Capabilities
- Extract Functional Requirements (FR-XXX) from unstructured text
- Extract Non-Functional Requirements (NFR-XXX)
- Identify Business Rules (BR-XXX)
- Detect assumptions and explicitly out-of-scope items
- Support input types: manual text, meeting transcript, chat log, markdown, email, audio transcript

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| raw_text | User input | Yes |
| project_name | Project record | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/requirements.md | Structured requirement summary with FR/NFR/BR IDs |

## Behaviour Notes
- Always assign sequential IDs (FR-001, FR-002, ...)
- Flag ambiguous requirements explicitly rather than guessing
- If input is too short (<100 words), request more detail
- Model: qwen3:8b (general reasoning)
""",

    "gap-analysis-agent": """\
# Gap Analysis Agent — Skill Document

## Role
Reviews the Requirement Summary to find gaps, ambiguities, conflicts, and missing
information before the BA Agent begins specification work.

## Layer
Business Layer — Step 2 of 12

## Capabilities
- Detect missing acceptance criteria per FR
- Identify conflicting requirements
- Flag under-specified NFRs (e.g. "fast" without a number)
- Generate open questions (OQ-XXX) that need stakeholder clarification
- Estimate risk level per gap (LOW / MEDIUM / HIGH)

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/requirements.md | Requirement Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/gap_report.md | Gap analysis with GAP-XXX IDs, risk levels, open questions |

## Behaviour Notes
- Be specific: reference the FR-XXX that each gap affects
- Do not invent requirements — only surface what is unclear
- A good gap report has 3–15 items; fewer suggests shallow analysis
- Model: qwen3.5:9b (larger context for thorough review)
""",

    "ba-agent": """\
# BA Agent — Skill Document

## Role
Translates requirements and gap analysis into a Functional Specification Document (FSD)
and User Stories with Acceptance Criteria, forming the contract for the Design Layer.

## Layer
Business Layer — Step 3 of 12

## Capabilities
- Write User Stories in standard format (As a / I want / So that)
- Define Acceptance Criteria per story (Given / When / Then)
- Produce a Functional Specification with screen-level behaviour
- Map every story back to a FR-XXX requirement ID
- Identify personas and user journeys

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/requirements.md | Requirement Agent | Yes |
| docs/gap_report.md | Gap Analysis Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/fsd.md | Functional Specification with AC per feature |
| docs/user_stories.md | US-XXX stories with Given/When/Then AC |

## Behaviour Notes
- Gate: output must be human-approved before Design Layer starts
- Each US must reference at least one FR-XXX
- FSD sections must align with screen specs the UX Agent will produce
- Model: qwen3.5:9b
""",

    "architect-agent": """\
# Solution Architect Agent — Skill Document

## Role
Designs the technical architecture, database schema, and API specification based on
the FSD and User Stories produced by the BA Agent.

## Layer
Design Layer — Step 4 of 12

## Capabilities
- Select appropriate tech stack (default: FastAPI + React + PostgreSQL)
- Design normalized database schema with tables, columns, indexes, FK constraints
- Define RESTful API endpoints with request/response schemas
- Produce component and deployment diagrams
- Identify integration points and third-party services

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/fsd.md | BA Agent | Yes |
| docs/user_stories.md | BA Agent | Yes |
| docs/requirements.md | Requirement Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/architecture.md | Tech stack, component diagram, deployment model |
| docs/db_schema.md | Tables, columns, types, indexes, FK constraints |
| docs/api_spec.md | OpenAPI-style endpoints with request/response |

## Behaviour Notes
- Default stack: FastAPI (Python 3.11) + React + Vite + PostgreSQL 15 + Redis
- Every DB table must have a UUID primary key and created_at/updated_at timestamps
- Every API endpoint must reference at least one FR-XXX
- Model: qwen3.5:9b
""",

    "ux-agent": """\
# UX Agent — Skill Document

## Role
Designs screen specifications and UX flows from the FSD and Architecture, giving the
Developer Agent precise UI requirements to implement.

## Layer
Design Layer — Step 5 of 12

## Capabilities
- Define screens with UI-XXX IDs
- Specify fields, actions, validation rules, and error states per screen
- Produce user journey flows in Mermaid diagram format
- Identify navigation patterns and state transitions
- Map every screen to a US-XXX user story

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/fsd.md | BA Agent | Yes |
| docs/user_stories.md | BA Agent | Yes |
| docs/architecture.md | SA Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/screen_spec.md | UI-XXX screens with fields, actions, validation |
| docs/ux_flows.md | User journeys in Mermaid flowchart format |

## Behaviour Notes
- Every field must have: label, type, required/optional, validation rule
- Every action must describe success state and error state
- Model: qwen3:8b
""",

    "developer-agent": """\
# Developer Agent — Skill Document

## Role
Generates real, runnable source code files for the application based on the Technical
Design task list, architecture, and screen specifications.

## Layer
Delivery Layer — Step 7 of 12

## Capabilities
- Generate FastAPI backend (routes, models, services, schemas)
- Generate React + TypeScript frontend (pages, components, hooks, API clients)
- Generate Alembic database migration files
- Two-phase generation: (1) plan file list, (2) generate each file
- Scalable: 1–3 parallel instances for large projects

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/dev_tasks.md | Technical Design Agent | Yes |
| docs/architecture.md | SA Agent | Yes |
| docs/db_schema.md | SA Agent | Yes |
| docs/api_spec.md | SA Agent | Yes |
| docs/screen_spec.md | UX Agent | Yes |

## Output Contract
| Path | Description |
|------|-------------|
| app/backend/** | FastAPI application files |
| app/frontend/** | React application files |
| app/db/migrations/** | Alembic migration files |

## Behaviour Notes
- Never use JSON mode (response_format=None) — outputs raw code
- Minimum 30 characters per file; retry once if below threshold
- Strips markdown code fences from LLM output
- Model: coder14b:latest (code-specialized)

## Scaling Rules
| Task Count | Instances |
|------------|-----------|
| ≤ 30 files | 1 instance |
| 31–80 files | 2 instances (backend + frontend) |
| > 80 files | 3 instances (backend + frontend + db/infra) |
""",

    "qa-agent": """\
# QA Agent — Skill Document

## Role
Generates actual test files (pytest, httpx, Playwright) and executes them against
the running application, producing a test report with pass/fail results.

## Layer
Delivery Layer — Step 9 of 12

## Capabilities
- Generate pytest unit test files per backend module
- Generate httpx integration tests per API endpoint
- Generate Playwright e2e tests per UI screen
- Execute tests inside Docker container
- Capture stdout/stderr and exit code
- Produce structured test report (pass/fail/coverage)

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| app/** | Developer Agent | Yes |
| docs/api_spec.md | SA Agent | Yes |
| docs/screen_spec.md | UX Agent | Yes |
| docs/user_stories.md | BA Agent | Yes |

## Output Contract
| Path | Description |
|------|-------------|
| tests/unit/test_*.py | pytest unit tests |
| tests/api/test_api_*.py | httpx integration tests |
| tests/e2e/test_*.spec.ts | Playwright UI tests |
| docs/test_report.md | Pass/fail summary with coverage |

## Behaviour Notes
- Gate: all tests pass → proceed; failures → human can override
- Model: qwen3:8b
""",

    "devops-agent": """\
# DevOps Agent — Skill Document

## Role
Generates deployment configuration files and executes the build + deploy pipeline,
including Docker image builds, health checks, and rollback on failure.

## Layer
Delivery Layer — Step 10 of 12

## Capabilities
- Generate multi-stage Dockerfile (backend + frontend)
- Generate docker-compose.yml (dev) and docker-compose.prod.yml (production)
- Generate nginx reverse proxy configuration
- Generate GitHub Actions CI/CD workflows
- Execute docker build + docker-compose up
- Health check: GET /health → 200
- Rollback: docker-compose down and restore previous image on failure

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/architecture.md | SA Agent | Yes |
| app/** | Developer Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| Dockerfile.backend | Multi-stage backend image |
| Dockerfile.frontend | Multi-stage frontend image |
| docker-compose.yml | Local development compose |
| docker-compose.prod.yml | Production compose with resource limits |
| nginx.conf | Reverse proxy configuration |
| .env.example | Environment variable template |
| .github/workflows/ci.yml | CI pipeline |
| .github/workflows/deploy.yml | Deploy pipeline |
| docs/build_report.md | Build + deploy result log |

## Behaviour Notes
- Never hardcode real passwords or secrets
- Health check must pass before marking step complete
- Gate: health check pass → proceed to Monitoring Agent
- Model: coder14b:latest
""",

    "change-impact-agent": """\
# Change Impact Agent — Skill Document

## Role
On-demand analysis agent. When a requirement changes after the pipeline has run,
identifies all affected documents, code files, and tests and estimates re-work cost.

## Layer
On-demand (not in auto-pipeline)

## Capabilities
- Diff original vs. updated requirements
- Map changed requirements to affected FSD sections, API endpoints, DB tables, screens
- Identify affected code files by module
- Identify affected test cases
- Estimate re-work in story points / sprint days
- Recommend which pipeline layer to re-run from

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| Original docs/requirements.md | Requirement Agent | Yes |
| Changed requirement text | User | Yes |
| All existing docs/** | Previous agents | Yes |
| app/** | Developer Agent | No (if code gen done) |

## Output Contract
| File | Description |
|------|-------------|
| docs/change_impact.md | Affected items, re-work estimate, recommended action |

## Behaviour Notes
- Triggered by user action, not automatically
- References FR-XXX, US-XXX, UI-XXX, API-XXX IDs in impact analysis
- Model: deepseek-r1:14b (reasoning-specialized for impact analysis)
""",

    "documentation-agent": """\
# Documentation Agent — Skill Document

## Role
Compiles all agent-generated documents into a single cohesive project documentation
package for stakeholder review and archival.

## Layer
On-demand (removed from auto-pipeline in Phase 3)

## Capabilities
- Aggregate documents from all previous agents
- Generate executive summary
- Produce table of contents with cross-references
- Export combined markdown document

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| All docs/** | All agents | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/compiled_docs.md | Full project documentation package |

## Behaviour Notes
- Call on-demand after pipeline completes
- Model: qwen3:8b
""",

    "pm-agent": """\
# PM Agent — Skill Document

## Role
Generates project management summary and delivery report including timeline,
resource allocation, risk assessment, and delivery status.

## Layer
On-demand (removed from auto-pipeline in Phase 3)

## Capabilities
- Summarize project scope and delivery status
- Generate sprint breakdown and timeline estimate
- Identify risks and mitigation strategies
- Produce stakeholder-ready delivery report

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| All docs/** | All agents | Yes |
| app/** | Developer Agent | No |

## Output Contract
| File | Description |
|------|-------------|
| docs/project_summary.md | Project overview and status |
| docs/delivery_report.md | Delivery timeline and risk register |

## Behaviour Notes
- Call on-demand after pipeline completes
- Model: qwen3:8b
""",
}


def upgrade() -> None:
    op.add_column("agents", sa.Column("skill_markdown", sa.Text(), nullable=True))

    for agent_name, skill_md in _SKILLS.items():
        escaped = skill_md.replace("'", "''")
        op.execute(f"""
            UPDATE agents
            SET skill_markdown = '{escaped}'
            WHERE name = '{agent_name}'
        """)


def downgrade() -> None:
    op.drop_column("agents", "skill_markdown")
