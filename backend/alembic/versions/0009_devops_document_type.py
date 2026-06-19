"""Add devops_config to document_type enum

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'devops_config'")

    # Seed devops-agent row if not already present
    op.execute("""
        INSERT INTO agents (name, role, home_zone, current_zone, model_provider, model_name, status, is_active)
        VALUES ('devops-agent', 'devops_engineer', 'devops_room', 'devops_room', 'ollama', 'coder14b:latest', 'idle', true)
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM agents WHERE name = 'devops-agent'")
    # PostgreSQL does not support removing enum values — no-op for the type
