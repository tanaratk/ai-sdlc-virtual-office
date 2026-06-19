"""Add technical_design document type and technical-design-agent seed

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TECH_SKILL = """\
# Technical Design Agent — Skill Document

## Role
Translates approved FSD, Architecture, API Spec, and Screen Spec into a detailed
dev_tasks.md — a file-level task breakdown that guides Developer Agent(s) on exactly
what to create, in what order, and for which requirement.

## Layer
Design Layer — Step 6 of 12

## Capabilities
- Break work into TASK-XXX items with file path, domain, and FR reference
- Estimate lines of code per task
- Identify task dependencies (depends_on)
- Tag tasks by domain: backend / frontend / database / test / infra
- Determine how many Developer Agent instances to spawn

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/fsd.md | BA Agent | Yes |
| docs/architecture.md | SA Agent | Yes |
| docs/db_schema.md | SA Agent | Yes |
| docs/api_spec.md | SA Agent | Yes |
| docs/screen_spec.md | UX Agent | Yes |

## Output Contract
| File | Description |
|------|-------------|
| docs/dev_tasks.md | TASK-XXX breakdown with file path, domain, FR-ref, dependencies |

## Behaviour Notes
- Gate: output must be human-approved before Delivery Layer starts
- Task count drives Developer Agent scaling (<=30: 1 instance, 31-80: 2, >80: 3)
- Model: qwen3.5:9b
"""


def upgrade() -> None:
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'technical_design'")

    escaped = _TECH_SKILL.replace("'", "''")
    op.execute(f"""
        INSERT INTO agents (name, role, home_zone, current_zone, model_provider, model_name, status, is_active, skill_markdown)
        VALUES (
            'technical-design-agent', 'technical_designer',
            'design_room', 'design_room',
            'ollama', 'qwen3.5:9b', 'idle', true,
            '{escaped}'
        )
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM agents WHERE name = 'technical-design-agent'")
