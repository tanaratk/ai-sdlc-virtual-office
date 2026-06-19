"""Add workspace_path to projects

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "workspace_path",
            sa.String(500),
            nullable=True,
            server_default=r"D:\workspace",
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "workspace_path")
