"""Add test_report document type

Revision ID: 0014
Revises: 0013
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'test_report'")


def downgrade() -> None:
    # PostgreSQL cannot drop enum values without rebuilding the type.
    pass
