"""Add MCP tool registry and call log tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE mcp_tool_category AS ENUM "
        "('filesystem','github','database','design','browser','document','testing')"
    )
    op.execute(
        "CREATE TYPE mcp_call_status AS ENUM "
        "('pending','approved','rejected','running','completed','failed')"
    )

    op.create_table(
        "mcp_tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tool_name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category",
                  postgresql.ENUM("filesystem","github","database","design",
                                  "browser","document","testing",
                                  name="mcp_tool_category", create_type=False),
                  nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_dangerous", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("server_config_json", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "mcp_tool_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("agents.id"), nullable=True),
        sa.Column("status",
                  postgresql.ENUM("pending","approved","rejected","running","completed","failed",
                                  name="mcp_call_status", create_type=False),
                  nullable=False, server_default="pending"),
        sa.Column("input_json", postgresql.JSON(), nullable=True),
        sa.Column("output_json", postgresql.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(255), nullable=True),
        sa.Column("resolved_by", sa.String(255), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_mcp_tool_calls_project_id", "mcp_tool_calls", ["project_id"])
    op.create_index("ix_mcp_tool_calls_status", "mcp_tool_calls", ["status"])

    # Seed default tools
    op.execute("""
        INSERT INTO mcp_tools
            (id, tool_name, display_name, description, category,
             requires_approval, is_enabled, is_dangerous)
        VALUES
            (gen_random_uuid(), 'github.create_issue',
             'GitHub — Create Issue',
             'Create a GitHub issue from a development task. Links to requirement IDs.',
             'github', false, true, false),

            (gen_random_uuid(), 'github.create_branch',
             'GitHub — Create Branch',
             'Create a new git branch in the connected repository.',
             'github', false, true, false),

            (gen_random_uuid(), 'github.list_issues',
             'GitHub — List Issues',
             'List open issues in the connected repository.',
             'github', false, true, false),

            (gen_random_uuid(), 'document.export_pdf',
             'Document — Export PDF',
             'Export a generated document to PDF format.',
             'document', false, false, false),

            (gen_random_uuid(), 'document.compile_all',
             'Document — Compile All',
             'Compile all project documents into a single file.',
             'document', false, false, false),

            (gen_random_uuid(), 'database.read_query',
             'Database — Read Query',
             'Execute a read-only SQL query against the project database.',
             'database', true, false, false),

            (gen_random_uuid(), 'filesystem.read_file',
             'Filesystem — Read File',
             'Read a file from the server filesystem. Requires approval.',
             'filesystem', true, false, true),

            (gen_random_uuid(), 'browser.fetch_url',
             'Browser — Fetch URL',
             'Fetch content from a URL. Requires approval.',
             'browser', true, false, false),

            (gen_random_uuid(), 'figma.get_design',
             'Figma — Get Design',
             'Fetch design context from a Figma file URL.',
             'design', false, false, false),

            (gen_random_uuid(), 'testing.run_suite',
             'Test Runner — Run Suite',
             'Execute a test suite. Requires approval to prevent unintended runs.',
             'testing', true, false, false)
    """)


def downgrade() -> None:
    op.drop_index("ix_mcp_tool_calls_status", table_name="mcp_tool_calls")
    op.drop_index("ix_mcp_tool_calls_project_id", table_name="mcp_tool_calls")
    op.drop_table("mcp_tool_calls")
    op.drop_table("mcp_tools")
    op.execute("DROP TYPE mcp_call_status")
    op.execute("DROP TYPE mcp_tool_category")
