"""Add diagram_spec document type

Revision ID: 0022
Revises: 0021
Create Date: 2026-06-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'diagram_spec'")


def downgrade() -> None:
    # PostgreSQL cannot drop enum values without rebuilding the type.
    pass
