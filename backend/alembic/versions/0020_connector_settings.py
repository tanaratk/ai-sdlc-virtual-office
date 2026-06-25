"""Add connector_settings table for MCP external tool credentials

Revision ID: 0020
Revises: 0019
Create Date: 2026-06-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "connector_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("connector_type", sa.String(length=50), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("extra_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_test_ok", sa.Boolean(), nullable=True),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connector_type"),
    )


def downgrade() -> None:
    op.drop_table("connector_settings")
