"""Initial schema — all 14 tables

Revision ID: 0001
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enums ──────────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE project_status AS ENUM ('active', 'archived', 'completed')")
    op.execute("CREATE TYPE input_type AS ENUM ('manual_text', 'meeting_transcript', 'chat_log', 'markdown_document', 'email_content', 'audio_transcript')")
    op.execute("CREATE TYPE agent_status AS ENUM ('idle', 'working', 'done', 'error')")
    op.execute("CREATE TYPE sprite_direction AS ENUM ('up', 'down', 'left', 'right')")
    op.execute("CREATE TYPE model_provider AS ENUM ('ollama', 'openai')")
    op.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed', 'cancelled')")
    op.execute("CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE pipeline_run_status AS ENUM ('pending', 'running', 'waiting_for_user', 'completed', 'failed', 'cancelled')")
    op.execute("CREATE TYPE pipeline_step_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped')")
    op.execute("""CREATE TYPE document_type AS ENUM (
        'requirement_summary', 'gap_analysis_report', 'brd', 'fsd', 'user_story',
        'architecture_design', 'database_design', 'api_spec', 'screen_spec',
        'code_task_list', 'test_cases', 'uat_script', 'change_impact_report',
        'compiled_documents', 'project_summary', 'delivery_report'
    )""")
    op.execute("CREATE TYPE document_status AS ENUM ('draft', 'review', 'approved', 'rejected', 'superseded')")
    op.execute("CREATE TYPE actor_type AS ENUM ('agent', 'user', 'system')")
    op.execute("CREATE TYPE message_type AS ENUM ('handoff', 'chat', 'notification', 'system')")
    op.execute("""CREATE TYPE event_type AS ENUM (
        'task_started', 'task_completed', 'task_failed',
        'agent_moved', 'document_created', 'document_approved', 'document_rejected',
        'pipeline_step_started', 'pipeline_step_completed',
        'handoff_sent', 'user_message'
    )""")
    op.execute("CREATE TYPE link_type AS ENUM ('derived_from', 'implements', 'tests', 'conflicts_with')")
    op.execute("CREATE TYPE artifact_type AS ENUM ('requirement_input', 'document', 'task', 'pipeline_step')")
    op.execute("CREATE TYPE memory_type AS ENUM ('context', 'decision', 'fact', 'instruction')")
    op.execute("CREATE TYPE sprint_status AS ENUM ('not_started', 'in_progress', 'done', 'overdue')")
    op.execute("CREATE TYPE milestone_status AS ENUM ('not_started', 'in_progress', 'done', 'overdue')")

    # ── Batch 1: No FK dependencies ────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.Enum("active", "archived", "completed", name="project_status"), nullable=False, server_default="active"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_projects_status", "projects", ["status"])

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("role", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("goal", sa.Text),
        sa.Column("system_prompt", sa.Text),
        sa.Column("avatar_url", sa.Text),
        sa.Column("home_zone", sa.String(100)),
        sa.Column("current_zone", sa.String(100)),
        sa.Column("status", sa.Enum("idle", "working", "done", "error", name="agent_status"), nullable=False, server_default="idle"),
        sa.Column("location_x", sa.Integer, nullable=False, server_default="0"),
        sa.Column("location_y", sa.Integer, nullable=False, server_default="0"),
        sa.Column("target_x", sa.Integer),
        sa.Column("target_y", sa.Integer),
        sa.Column("sprite_direction", sa.Enum("up", "down", "left", "right", name="sprite_direction"), nullable=False, server_default="down"),
        sa.Column("model_provider", sa.Enum("ollama", "openai", name="model_provider"), nullable=False, server_default="ollama"),
        sa.Column("model_name", sa.String(100), nullable=False, server_default="qwen3:8b"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_agents_status", "agents", ["status"])
    op.create_index("idx_agents_is_active", "agents", ["is_active"])

    op.create_table(
        "llm_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider", sa.Enum("ollama", "openai", name="model_provider"), nullable=False),
        sa.Column("base_url", sa.Text),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("api_key_encrypted", sa.Text),
        sa.Column("temperature", sa.Float, nullable=False, server_default="0.7"),
        sa.Column("max_tokens", sa.Integer, nullable=False, server_default="4096"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_llm_settings_is_active", "llm_settings", ["is_active"])

    # ── Batch 2: FK → projects or agents ──────────────────────────────────────
    op.create_table(
        "requirement_inputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("input_type", sa.Enum("manual_text", "meeting_transcript", "chat_log", "markdown_document", "email_content", "audio_transcript", name="input_type"), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("file_url", sa.Text),
        sa.Column("source_owner", sa.String(255)),
        sa.Column("source_date", sa.TIMESTAMP(timezone=True)),
        sa.Column("metadata_json", postgresql.JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_requirement_inputs_project_id", "requirement_inputs", ["project_id"])
    op.create_index("idx_requirement_inputs_input_type", "requirement_inputs", ["input_type"])

    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "waiting_for_user", "completed", "failed", "cancelled", name="pipeline_run_status"), nullable=False, server_default="pending"),
        sa.Column("current_step", sa.String(100)),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_pipeline_runs_project_id", "pipeline_runs", ["project_id"])
    op.create_index("idx_pipeline_runs_status", "pipeline_runs", ["status"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.Enum(
            "requirement_summary", "gap_analysis_report", "brd", "fsd", "user_story",
            "architecture_design", "database_design", "api_spec", "screen_spec",
            "code_task_list", "test_cases", "uat_script", "change_impact_report",
            "compiled_documents", "project_summary", "delivery_report",
            name="document_type"
        ), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content_markdown", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("status", sa.Enum("draft", "review", "approved", "rejected", "superseded", name="document_status"), nullable=False, server_default="draft"),
        sa.Column("created_by_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("approved_by", sa.String(255)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_documents_project_id", "documents", ["project_id"])
    op.create_index("idx_documents_document_type", "documents", ["document_type"])
    op.create_index("idx_documents_status", "documents", ["status"])

    op.create_table(
        "agent_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.Enum("context", "decision", "fact", "instruction", name="memory_type"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding_id", sa.String(255)),
        sa.Column("importance_score", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_agent_memories_agent_id", "agent_memories", ["agent_id"])
    op.create_index("idx_agent_memories_project_id", "agent_memories", ["project_id"])

    op.create_table(
        "sprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sprint_number", sa.Integer, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("planned_start", sa.Date, nullable=False),
        sa.Column("planned_end", sa.Date, nullable=False),
        sa.Column("actual_end", sa.Date),
        sa.Column("status", sa.Enum("not_started", "in_progress", "done", "overdue", name="sprint_status"), nullable=False, server_default="not_started"),
        sa.Column("story_points_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("story_points_done", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("project_id", "sprint_number"),
    )
    op.create_index("idx_sprints_project_id", "sprints", ["project_id"])
    op.create_index("idx_sprints_status", "sprints", ["status"])

    op.create_table(
        "milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("target_date", sa.Date, nullable=False),
        sa.Column("actual_date", sa.Date),
        sa.Column("status", sa.Enum("not_started", "in_progress", "done", "overdue", name="milestone_status"), nullable=False, server_default="not_started"),
        sa.Column("mvp_number", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_milestones_project_id", "milestones", ["project_id"])

    # ── Batch 3: FK → requirement_inputs or pipeline_runs ─────────────────────
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("status", sa.Enum("pending", "in_progress", "done", "failed", "cancelled", name="task_status"), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Enum("low", "medium", "high", "critical", name="task_priority"), nullable=False, server_default="medium"),
        sa.Column("pipeline_step", sa.String(100)),
        sa.Column("input_reference_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("requirement_inputs.id", ondelete="SET NULL")),
        sa.Column("output_document_id", postgresql.UUID(as_uuid=True)),
        sa.Column("due_date", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_tasks_project_id", "tasks", ["project_id"])
    op.create_index("idx_tasks_status", "tasks", ["status"])

    op.create_table(
        "pipeline_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pipeline_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_name", sa.String(100), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", "skipped", name="pipeline_step_status"), nullable=False, server_default="pending"),
        sa.Column("input_json", postgresql.JSONB),
        sa.Column("output_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="SET NULL")),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("error_message", sa.Text),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("idx_pipeline_steps_pipeline_run_id", "pipeline_steps", ["pipeline_run_id"])
    op.create_index("idx_pipeline_steps_status", "pipeline_steps", ["status"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="SET NULL")),
        sa.Column("sender_type", sa.Enum("agent", "user", "system", name="actor_type"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receiver_type", sa.Enum("agent", "user", "system", name="actor_type"), nullable=False),
        sa.Column("receiver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("message_type", sa.Enum("handoff", "chat", "notification", "system", name="message_type"), nullable=False, server_default="chat"),
        sa.Column("metadata_json", postgresql.JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_messages_project_id", "messages", ["project_id"])

    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="SET NULL")),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("event_type", sa.Enum(
            "task_started", "task_completed", "task_failed",
            "agent_moved", "document_created", "document_approved", "document_rejected",
            "pipeline_step_started", "pipeline_step_completed",
            "handoff_sent", "user_message",
            name="event_type"
        ), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("metadata_json", postgresql.JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_activity_logs_project_id", "activity_logs", ["project_id"])
    op.create_index("idx_activity_logs_created_at", "activity_logs", ["created_at"])

    op.create_table(
        "traceability_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.Enum("requirement_input", "document", "task", "pipeline_step", name="artifact_type"), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.Enum("requirement_input", "document", "task", "pipeline_step", name="artifact_type"), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("link_type", sa.Enum("derived_from", "implements", "tests", "conflicts_with", name="link_type"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_traceability_links_project_id", "traceability_links", ["project_id"])


def downgrade() -> None:
    for table in [
        "traceability_links", "activity_logs", "messages",
        "pipeline_steps", "tasks", "milestones", "sprints",
        "agent_memories", "documents", "pipeline_runs",
        "requirement_inputs", "llm_settings", "agents", "projects",
    ]:
        op.drop_table(table)

    for enum in [
        "artifact_type", "link_type", "memory_type",
        "milestone_status", "sprint_status", "event_type",
        "message_type", "actor_type", "document_status", "document_type",
        "pipeline_step_status", "pipeline_run_status",
        "task_priority", "task_status", "model_provider",
        "sprite_direction", "agent_status", "input_type", "project_status",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
