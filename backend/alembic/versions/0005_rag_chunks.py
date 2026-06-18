"""Add rag_chunks table for RAG ingestion and search

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rag_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_rag_chunks_project_id", "rag_chunks", ["project_id"])
    op.create_index("ix_rag_chunks_document_id", "rag_chunks", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_rag_chunks_document_id", table_name="rag_chunks")
    op.drop_index("ix_rag_chunks_project_id", table_name="rag_chunks")
    op.drop_table("rag_chunks")
