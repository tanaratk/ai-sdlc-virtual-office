"""Add figma.get_node + figma.push_comment MCP tools; enable all figma tools

Revision ID: 0023
Revises: 0022
Create Date: 2026-06-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0023"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable figma.get_design (was seeded as disabled)
    op.execute(
        "UPDATE mcp_tools SET is_enabled = true WHERE tool_name = 'figma.get_design'"
    )

    # Add figma.get_node
    op.execute(
        """
        INSERT INTO mcp_tools (id, tool_name, display_name, description, category,
                               is_enabled, is_dangerous, requires_approval)
        VALUES (gen_random_uuid(), 'figma.get_node',
                'Figma -- Get Node',
                'Fetch details of a specific Figma node by its node_id.',
                'design', true, false, false)
        ON CONFLICT (tool_name) DO NOTHING
        """
    )

    # Add figma.push_comment
    op.execute(
        """
        INSERT INTO mcp_tools (id, tool_name, display_name, description, category,
                               is_enabled, is_dangerous, requires_approval)
        VALUES (gen_random_uuid(), 'figma.push_comment',
                'Figma -- Push Comment',
                'Post a comment on the linked Figma file (e.g. screen spec annotations).',
                'design', true, false, true)
        ON CONFLICT (tool_name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM mcp_tools WHERE tool_name IN ('figma.get_node', 'figma.push_comment')")
    op.execute("UPDATE mcp_tools SET is_enabled = false WHERE tool_name = 'figma.get_design'")
