import uuid
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy import Column, UniqueConstraint
from sqlmodel import Field, SQLModel


# โ”€โ”€ Enums โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class ProjectStatus(str, Enum):
    active = "active"
    archived = "archived"
    completed = "completed"


class InputType(str, Enum):
    manual_text = "manual_text"
    meeting_transcript = "meeting_transcript"
    chat_log = "chat_log"
    markdown_document = "markdown_document"
    email_content = "email_content"
    audio_transcript = "audio_transcript"


class AgentStatus(str, Enum):
    idle = "idle"
    working = "working"
    done = "done"
    error = "error"


class SpriteDirection(str, Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"


class ModelProvider(str, Enum):
    ollama = "ollama"
    openai = "openai"
    anthropic = "anthropic"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class PipelineRunStatus(str, Enum):
    pending = "pending"
    running = "running"
    waiting_for_user = "waiting_for_user"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PipelineStepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class DocumentType(str, Enum):
    requirement_summary = "requirement_summary"
    gap_analysis_report = "gap_analysis_report"
    brd = "brd"
    fsd = "fsd"
    user_story = "user_story"
    architecture_design = "architecture_design"
    database_design = "database_design"
    api_spec = "api_spec"
    screen_spec = "screen_spec"
    code_task_list = "code_task_list"
    technical_design = "technical_design"
    code_review = "code_review"
    devops_config = "devops_config"
    build_report = "build_report"
    monitoring_report = "monitoring_report"
    test_cases = "test_cases"
    test_report = "test_report"
    uat_script = "uat_script"
    change_impact_report = "change_impact_report"
    compiled_documents = "compiled_documents"
    project_summary = "project_summary"
    delivery_report = "delivery_report"


class DocumentStatus(str, Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    rejected = "rejected"
    superseded = "superseded"


class ActorType(str, Enum):
    agent = "agent"
    user = "user"
    system = "system"


class MessageType(str, Enum):
    handoff = "handoff"
    chat = "chat"
    notification = "notification"
    system = "system"


class EventType(str, Enum):
    task_started = "task_started"
    task_completed = "task_completed"
    task_failed = "task_failed"
    agent_moved = "agent_moved"
    document_created = "document_created"
    document_approved = "document_approved"
    document_rejected = "document_rejected"
    pipeline_step_started = "pipeline_step_started"
    pipeline_step_completed = "pipeline_step_completed"
    handoff_sent = "handoff_sent"
    user_message = "user_message"


class LinkType(str, Enum):
    derived_from = "derived_from"
    implements = "implements"
    tests = "tests"
    conflicts_with = "conflicts_with"


class ArtifactType(str, Enum):
    requirement_input = "requirement_input"
    document = "document"
    task = "task"
    pipeline_step = "pipeline_step"


class MemoryType(str, Enum):
    context = "context"
    decision = "decision"
    fact = "fact"
    instruction = "instruction"


class SprintStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


class MilestoneStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


# โ”€โ”€ Models โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    name: str = Field(max_length=255)
    hashed_password: str
    role: str = Field(default="user", max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.active)
    created_by: str = Field(max_length=255)
    workspace_path: Optional[str] = Field(default="D:\\workspace", max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RequirementInput(SQLModel, table=True):
    __tablename__ = "requirement_inputs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    input_type: InputType
    title: Optional[str] = Field(default=None, max_length=255)
    content: str
    file_url: Optional[str] = Field(default=None)
    source_owner: Optional[str] = Field(default=None, max_length=255)
    source_date: Optional[datetime] = Field(default=None)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True)
    role: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    goal: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    home_zone: Optional[str] = Field(default=None, max_length=100)
    current_zone: Optional[str] = Field(default=None, max_length=100)
    status: AgentStatus = Field(default=AgentStatus.idle)
    location_x: int = Field(default=0)
    location_y: int = Field(default=0)
    target_x: Optional[int] = Field(default=None)
    target_y: Optional[int] = Field(default=None)
    sprite_direction: SpriteDirection = Field(default=SpriteDirection.down)
    model_provider: ModelProvider = Field(default=ModelProvider.ollama)
    model_name: str = Field(default="qwen3:8b", max_length=100)
    skill_markdown: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    assigned_agent_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="agents.id"
    )
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    pipeline_step: Optional[str] = Field(default=None, max_length=100)
    input_reference_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="requirement_inputs.id"
    )
    output_document_id: Optional[uuid.UUID] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    created_by: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PipelineRun(SQLModel, table=True):
    __tablename__ = "pipeline_runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    status: PipelineRunStatus = Field(default=PipelineRunStatus.pending)
    current_step: Optional[str] = Field(default=None, max_length=100)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    document_type: DocumentType
    title: str = Field(max_length=255)
    content_markdown: str
    version: int = Field(default=1)
    status: DocumentStatus = Field(default=DocumentStatus.draft)
    created_by_agent_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="agents.id"
    )
    approved_by: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PipelineStep(SQLModel, table=True):
    __tablename__ = "pipeline_steps"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pipeline_run_id: uuid.UUID = Field(foreign_key="pipeline_runs.id")
    step_name: str = Field(max_length=100)
    agent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="agents.id")
    status: PipelineStepStatus = Field(default=PipelineStepStatus.pending)
    input_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    output_document_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="documents.id"
    )
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
    sender_type: ActorType
    sender_id: uuid.UUID
    receiver_type: ActorType
    receiver_id: uuid.UUID
    content: str
    message_type: MessageType = Field(default=MessageType.chat)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
    agent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="agents.id")
    event_type: EventType
    message: str
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TraceabilityLink(SQLModel, table=True):
    __tablename__ = "traceability_links"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    source_type: ArtifactType
    source_id: uuid.UUID
    target_type: ArtifactType
    target_id: uuid.UUID
    link_type: LinkType
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LlmSetting(SQLModel, table=True):
    __tablename__ = "llm_settings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    provider: ModelProvider
    base_url: Optional[str] = Field(default=None)
    model_name: str = Field(max_length=100)
    api_key_encrypted: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=4096)
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentMemory(SQLModel, table=True):
    __tablename__ = "agent_memories"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_id: uuid.UUID = Field(foreign_key="agents.id")
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    memory_type: MemoryType
    content: str
    embedding_id: Optional[str] = Field(default=None, max_length=255)
    importance_score: float = Field(default=0.5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Sprint(SQLModel, table=True):
    __tablename__ = "sprints"
    __table_args__ = (UniqueConstraint("project_id", "sprint_number"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    sprint_number: int
    name: str = Field(max_length=255)
    planned_start: date
    planned_end: date
    actual_end: Optional[date] = Field(default=None)
    status: SprintStatus = Field(default=SprintStatus.not_started)
    story_points_total: int = Field(default=0)
    story_points_done: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Milestone(SQLModel, table=True):
    __tablename__ = "milestones"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    target_date: date
    actual_date: Optional[date] = Field(default=None)
    status: MilestoneStatus = Field(default=MilestoneStatus.not_started)
    mvp_number: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class McpToolCategory(str, Enum):
    filesystem = "filesystem"
    github = "github"
    database = "database"
    design = "design"
    browser = "browser"
    document = "document"
    testing = "testing"


class McpCallStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    running = "running"
    completed = "completed"
    failed = "failed"


class McpTool(SQLModel, table=True):
    __tablename__ = "mcp_tools"
    __table_args__ = (UniqueConstraint("tool_name"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tool_name: str = Field(max_length=100)
    display_name: str = Field(max_length=255)
    description: str
    category: McpToolCategory
    requires_approval: bool = Field(default=True)
    is_enabled: bool = Field(default=True)
    is_dangerous: bool = Field(default=False)
    server_config_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class McpToolCall(SQLModel, table=True):
    __tablename__ = "mcp_tool_calls"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    tool_name: str = Field(max_length=100)
    agent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="agents.id")
    status: McpCallStatus = Field(default=McpCallStatus.pending)
    input_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    output_json: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(sa.JSON)
    )
    error_message: Optional[str] = Field(default=None)
    requested_by: Optional[str] = Field(default=None, max_length=255)
    resolved_by: Optional[str] = Field(default=None, max_length=255)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: Optional[datetime] = Field(default=None)


class GitHubSetting(SQLModel, table=True):
    __tablename__ = "github_settings"
    __table_args__ = (UniqueConstraint("project_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    repo_owner: str = Field(max_length=255)
    repo_name: str = Field(max_length=255)
    access_token: str
    default_branch: str = Field(default="main", max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GitHubIssue(SQLModel, table=True):
    __tablename__ = "github_issues"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    issue_number: int
    issue_url: str = Field(max_length=500)
    title: str = Field(max_length=500)
    requirement_ids: Optional[str] = Field(default=None, max_length=500)
    state: str = Field(default="open", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RagChunk(SQLModel, table=True):
    __tablename__ = "rag_chunks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    document_id: uuid.UUID = Field(foreign_key="documents.id")
    document_type: str = Field(max_length=100)
    chunk_index: int
    chunk_text: str
    embedding_json: Optional[str] = Field(default=None, sa_column=Column(sa.Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
