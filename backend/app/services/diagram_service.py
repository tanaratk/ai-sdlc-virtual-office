"""Diagram generation service — calls the LLM to produce Mermaid diagram code."""
import json
import logging
import re

from app.llm import client as _llm

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert software architect specialising in technical diagrams.
Generate clean, valid Mermaid diagram code from project documentation.

Rules:
- Output ONLY valid Mermaid syntax (no markdown fences, no explanations)
- Use simple, descriptive node names without special characters
- Keep diagrams focused and readable (max 20 nodes)
- For architecture diagrams use flowchart TD
- For ERD use erDiagram with only the main entities and key relationships
- Do not include SQL keywords; use standard ERD notation"""

_USER_PROMPT_TEMPLATE = """Generate two Mermaid diagrams for this project:

### Architecture Design Document
{architecture}

### Database Design Document
{database}

Return a JSON object with exactly two keys:
{{
  "architecture_mermaid": "<valid mermaid flowchart code only>",
  "erd_mermaid": "<valid mermaid erDiagram code only>"
}}"""


def _clean_mermaid(code: str) -> str:
    """Strip markdown fences if LLM included them."""
    code = re.sub(r"^```(?:mermaid)?\s*", "", code.strip(), flags=re.MULTILINE)
    code = re.sub(r"\s*```$", "", code.strip(), flags=re.MULTILINE)
    return code.strip()


def generate_diagrams(
    architecture_doc: str,
    database_doc: str,
    model: str = "qwen3:8b",
) -> dict[str, str]:
    """
    Call the LLM and return {architecture_mermaid, erd_mermaid}.
    Falls back to stub diagrams if LLM fails or produces invalid JSON.
    """
    user_prompt = _USER_PROMPT_TEMPLATE.format(
        architecture=architecture_doc[:4000],
        database=database_doc[:4000],
    )

    try:
        raw = _llm.call(
            model=model,
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_format="json",
        )
        data = json.loads(raw)
        arch = _clean_mermaid(str(data.get("architecture_mermaid", "")))
        erd  = _clean_mermaid(str(data.get("erd_mermaid", "")))
    except Exception as exc:
        logger.warning("Diagram LLM call failed: %s — using stubs", exc)
        arch = _stub_architecture()
        erd  = _stub_erd()

    # Validate: must start with a known Mermaid diagram type
    if not _valid_mermaid(arch):
        arch = _stub_architecture()
    if not _valid_mermaid(erd):
        erd = _stub_erd()

    return {"architecture_mermaid": arch, "erd_mermaid": erd}


def _valid_mermaid(code: str) -> bool:
    keywords = ("flowchart", "graph", "sequenceDiagram", "classDiagram",
                 "erDiagram", "stateDiagram", "gantt", "pie", "mindmap")
    first = code.strip().split()[0] if code.strip() else ""
    return any(first.lower().startswith(k.lower()) for k in keywords)


def _stub_architecture() -> str:
    return """flowchart TD
    Client["Client Browser"] --> Frontend["Frontend\\n(React + Vite)"]
    Frontend --> API["Backend API\\n(FastAPI)"]
    API --> DB[("Database\\n(PostgreSQL)")]
    API --> LLM["LLM Provider\\n(Ollama / OpenAI)"]
    API --> Cache["Cache\\n(Redis)"]"""


def _stub_erd() -> str:
    return """erDiagram
    PROJECT {
        uuid id PK
        string name
        string status
    }
    DOCUMENT {
        uuid id PK
        uuid project_id FK
        string document_type
        string title
    }
    PIPELINE_RUN {
        uuid id PK
        uuid project_id FK
        string status
    }
    PROJECT ||--o{ DOCUMENT : "has"
    PROJECT ||--o{ PIPELINE_RUN : "triggers"
    PIPELINE_RUN ||--o{ DOCUMENT : "produces" """


def mermaid_to_drawio_url(mermaid_code: str) -> str:
    """Return a Mermaid Live Editor URL with the diagram pre-loaded."""
    import base64
    import urllib.parse
    payload = json.dumps({"code": mermaid_code, "mermaid": {"theme": "default"}})
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    return f"https://mermaid.live/edit#{encoded}"


def wrap_in_markdown(mermaid_code: str) -> str:
    return f"```mermaid\n{mermaid_code}\n```"
