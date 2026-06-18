"""Seed data — 10 agents + default LLM setting

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENTS = [
    ("requirement-agent",    "requirement_analyst",    "requirement_room"),
    ("gap-analysis-agent",   "gap_analyst",            "gap_analysis_room"),
    ("ba-agent",             "business_analyst",       "ba_room"),
    ("architect-agent",      "solution_architect",     "sa_room"),
    ("ux-agent",             "ux_designer",            "ux_studio"),
    ("developer-agent",      "developer",              "developer_zone"),
    ("qa-agent",             "qa_engineer",            "qa_lab"),
    ("change-impact-agent",  "change_analyst",         "change_impact_room"),
    ("documentation-agent",  "documentation_manager",  "documentation_room"),
    ("pm-agent",             "project_manager",        "pm_room"),
]


def upgrade() -> None:
    for name, role, zone in AGENTS:
        op.execute(f"""
            INSERT INTO agents (name, role, home_zone, current_zone, model_provider, model_name, status, is_active)
            VALUES ('{name}', '{role}', '{zone}', '{zone}', 'ollama', 'qwen3:8b', 'idle', true)
        """)

    op.execute("""
        INSERT INTO llm_settings (provider, base_url, model_name, temperature, max_tokens, is_active)
        VALUES ('ollama', 'http://localhost:11434', 'qwen3:8b', 0.7, 4096, true)
    """)


def downgrade() -> None:
    for name, _, _ in AGENTS:
        op.execute(f"DELETE FROM agents WHERE name = '{name}'")
    op.execute("DELETE FROM llm_settings WHERE provider = 'ollama' AND model_name = 'qwen3:8b'")
