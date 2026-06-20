"""Add monitoring_report document type and monitoring-agent seed

Revision ID: 0016
Revises: 0015
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SKILL = """\
# Monitoring Agent — Skill Document

## Role
Checks the deployed application after DevOps finishes and produces an initial
monitoring_report.md with endpoint health, Docker container status, and basic
runtime observations.

## Layer
Delivery Layer — Step 11 of 12

## Capabilities
- Probe common health endpoints after deployment
- Inspect Docker Compose service status when Docker is available
- Capture container list and recent logs
- Identify unhealthy or restarted containers
- Produce docs/monitoring_report.md

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| docs/build_report.md | DevOps Agent | Yes |
| Running Docker services | DevOps Agent | No |
| docs/api_spec.md | SA Agent | No |

## Output Contract
| File | Description |
|------|-------------|
| docs/monitoring_report.md | Initial post-deploy monitoring report |

## Behaviour Notes
- Best-effort: if Docker is unavailable, report skipped checks instead of failing the pipeline
- Health checks should include HTTP status and latency where possible
- Model: qwen3:8b
"""


def upgrade() -> None:
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'monitoring_report'")

    escaped = _SKILL.replace("'", "''")
    op.execute(f"""
        INSERT INTO agents (name, role, home_zone, current_zone, model_provider, model_name, status, is_active, skill_markdown)
        VALUES (
            'monitoring-agent', 'monitoring_engineer',
            'monitoring_room', 'monitoring_room',
            'ollama', 'qwen3:8b', 'idle', true,
            '{escaped}'
        )
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM agents WHERE name = 'monitoring-agent'")
