"""Add drawio MCP tools

Revision ID: 0024
Revises: 0023
Create Date: 2026-06-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0024"
down_revision: Union[str, None] = "0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ADD VALUE cannot use the new value in the same transaction.
    # Run it in AUTOCOMMIT so the value is visible immediately.
    conn = op.get_bind()
    conn.execute(sa.text("COMMIT"))
    conn.execute(sa.text("ALTER TYPE mcp_tool_category ADD VALUE IF NOT EXISTS 'drawio'"))
    conn.execute(sa.text("BEGIN"))

    op.execute(
        """
        INSERT INTO mcp_tools (id, tool_name, display_name, description, category,
                               is_enabled, is_dangerous, requires_approval)
        VALUES (gen_random_uuid(), 'drawio.list_diagrams',
                'Draw.io -- List Diagrams',
                'List all generated Mermaid diagrams for the current project.',
                'drawio', true, false, false)
        ON CONFLICT (tool_name) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO mcp_tools (id, tool_name, display_name, description, category,
                               is_enabled, is_dangerous, requires_approval)
        VALUES (gen_random_uuid(), 'drawio.export_diagram',
                'Draw.io -- Export Diagram',
                'Export a project diagram as Draw.io XML that can be opened in app.diagrams.net.',
                'drawio', true, false, false)
        ON CONFLICT (tool_name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM mcp_tools WHERE tool_name IN ('drawio.list_diagrams', 'drawio.export_diagram')"
    )
