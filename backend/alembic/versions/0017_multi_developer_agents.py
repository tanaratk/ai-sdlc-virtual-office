"""Seed multi-developer fan-out agent rows

Revision ID: 0017
Revises: 0016
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_AGENTS = [
    (
        "developer-agent-backend",
        "backend_developer",
        "Backend Developer Agent",
        "Owns FastAPI routes, SQLModel models, schemas, migrations, and backend integration files.",
    ),
    (
        "developer-agent-frontend",
        "frontend_developer",
        "Frontend Developer Agent",
        "Owns React/Vite pages, components, TypeScript types, and API client files.",
    ),
    (
        "developer-agent-platform",
        "platform_developer",
        "Platform Developer Agent",
        "Owns project configuration, README, environment files, tests, infra, and cross-cutting glue.",
    ),
]


def upgrade() -> None:
    for name, role, title, goal in _AGENTS:
        skill = f"""# {title}

## Role
Participates in the Developer Agent fan-out lane for large generated applications.

## Layer
Delivery Layer -- Step 7 of 12

## Focus
{goal}

## Behaviour Notes
- Works under the main developer-agent orchestrator
- Writes files into generated_app/
- Keeps imports and contracts consistent with files from other developer lanes
- Model: qwen3:8b
"""
        escaped = skill.replace("'", "''")
        op.execute(f"""
            INSERT INTO agents (
                name, role, description, goal, home_zone, current_zone,
                model_provider, model_name, status, is_active, skill_markdown
            )
            VALUES (
                '{name}', '{role}', '{title}', '{goal}',
                'developer_zone', 'developer_zone',
                'ollama', 'qwen3:8b', 'idle', true, '{escaped}'
            )
            ON CONFLICT (name) DO UPDATE SET
                role = EXCLUDED.role,
                description = EXCLUDED.description,
                goal = EXCLUDED.goal,
                home_zone = EXCLUDED.home_zone,
                current_zone = EXCLUDED.current_zone,
                skill_markdown = EXCLUDED.skill_markdown
        """)


def downgrade() -> None:
    for name, *_ in _AGENTS:
        op.execute(f"DELETE FROM agents WHERE name = '{name}'")
