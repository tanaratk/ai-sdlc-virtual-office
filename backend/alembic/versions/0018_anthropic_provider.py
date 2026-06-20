"""Add anthropic to model_provider enum

Revision ID: 0018
Revises: 0017
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE model_provider ADD VALUE IF NOT EXISTS 'anthropic'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values; downgrade is a no-op
    pass
