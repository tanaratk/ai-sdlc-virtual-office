"""Ensure devops-agent row exists in agents table

Sprint 27 added the devops-agent seed inside migration 0009 alongside an
ALTER TYPE statement. If that migration ran before the INSERT was added, or
if the transaction was rolled back for any reason, the agent row is missing.
This migration guarantees it exists as a standalone, idempotent operation.

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO agents (name, role, home_zone, current_zone, model_provider, model_name, status, is_active)
        VALUES ('devops-agent', 'devops_engineer', 'devops_room', 'devops_room', 'ollama', 'coder14b:latest', 'idle', true)
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM agents WHERE name = 'devops-agent'")
