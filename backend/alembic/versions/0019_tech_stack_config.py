"""Add tech_stack to projects and project_context_snapshot to pipeline_runs

Revision ID: 0019
Revises: 0018
Create Date: 2026-06-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("tech_stack", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "pipeline_runs",
        sa.Column("project_context_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("pipeline_runs", "project_context_snapshot")
    op.drop_column("projects", "tech_stack")
