"""Set per-agent default LLM model based on capability requirements

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Map agent name → recommended model based on spec Section 33
AGENT_MODELS = [
    ("developer-agent",     "coder14b:latest"),   # code-specific 14.8B, 128k ctx
    ("gap-analysis-agent",  "qwen3.5:9b"),        # 262k context for large requirement docs
    ("ba-agent",            "qwen3.5:9b"),         # large context for multi-source processing
    ("architect-agent",     "qwen3.5:9b"),         # architecture reasoning needs big context
    ("change-impact-agent", "deepseek-r1:14b"),    # reasoning model for complex impact analysis
]


def upgrade() -> None:
    for agent_name, model_name in AGENT_MODELS:
        op.execute(
            f"UPDATE agents SET model_name = '{model_name}' WHERE name = '{agent_name}'"
        )


def downgrade() -> None:
    for agent_name, _ in AGENT_MODELS:
        op.execute(
            f"UPDATE agents SET model_name = 'qwen3:8b' WHERE name = '{agent_name}'"
        )
