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


class DiagramGenerationError(Exception):
    """Raised when the LLM fails to generate valid Mermaid diagrams."""


def generate_diagrams(
    architecture_doc: str,
    database_doc: str,
    model: str = "qwen3:8b",
) -> dict[str, str]:
    """
    Call the LLM and return {architecture_mermaid, erd_mermaid}.
    Raises DiagramGenerationError if LLM fails or returns invalid Mermaid syntax.
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
        logger.error("Diagram LLM call failed: %s", exc)
        raise DiagramGenerationError(
            f"LLM failed to generate diagrams: {exc}. "
            "Check that the LLM service is running and the model is available."
        ) from exc

    if not _valid_mermaid(arch):
        raise DiagramGenerationError(
            "LLM returned invalid architecture diagram syntax. "
            "Try again or check that the Solution Architect documents contain sufficient detail."
        )
    if not _valid_mermaid(erd):
        raise DiagramGenerationError(
            "LLM returned invalid ERD syntax. "
            "Try again or check that the database design document is available."
        )

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


def extract_mermaid(content: str) -> str:
    """Extract raw Mermaid code from a fenced markdown block."""
    m = re.search(r"```(?:mermaid)?\s*\n?([\s\S]+?)\n?```", content)
    return m.group(1).strip() if m else content.strip()


def mermaid_to_drawio_xml(mermaid_code: str) -> str:
    """Convert basic Mermaid flowchart / erDiagram to Draw.io XML (mxGraphModel)."""
    import re

    lines = [l.strip() for l in mermaid_code.strip().splitlines() if l.strip()]
    nodes: dict[str, str] = {}   # id -> label
    edges: list[tuple[str, str, str]] = []  # (src, tgt, label)
    is_er = lines[0].lower().startswith("erdiagram") if lines else False

    if is_er:
        # erDiagram: entity names are words followed by { block, or on relation lines
        for line in lines[1:]:
            # Entity block: EntityName {
            m = re.match(r"^([A-Z][A-Za-z0-9_]*)\s*\{", line)
            if m:
                nodes[m.group(1)] = m.group(1)
                continue
            # Relation: EntityA ||--o{ EntityB : "label"
            m = re.match(r'^([A-Z][A-Za-z0-9_]+)\s+[|o}{]+[-–]+[|o}{]+\s+([A-Z][A-Za-z0-9_]+)\s*:\s*"?([^"]*)"?', line)
            if m:
                src, tgt, lbl = m.group(1), m.group(2), m.group(3).strip()
                if src not in nodes:
                    nodes[src] = src
                if tgt not in nodes:
                    nodes[tgt] = tgt
                edges.append((src, tgt, lbl))
    else:
        for line in lines[1:]:
            # Edge with label: A -->|label| B  or  A -- label --> B
            m = re.match(r'^(\w+)\s*--+>?\|([^|]*)\|\s*(\w+)', line)
            if m:
                src, lbl, tgt = m.group(1), m.group(2).strip(), m.group(3)
                edges.append((src, tgt, lbl))
                for n in (src, tgt):
                    if n not in nodes:
                        nodes[n] = n
                continue
            # Simple edge: A --> B or A --- B
            m = re.match(r'^(\w+)\s*[-]+>?\s*(\w+)', line)
            if m:
                src, tgt = m.group(1), m.group(2)
                edges.append((src, tgt, ""))
                for n in (src, tgt):
                    if n not in nodes:
                        nodes[n] = n
                continue
            # Node with label: A[Label] B(Label) C{Label} D[(Label)]
            m = re.match(r'^(\w+)\s*[\[\(\{]+\(?(.+?)\)?\s*[\]\)\}]+$', line)
            if m:
                nodes[m.group(1)] = m.group(2).strip()

    cell_w, cell_h = 130, 60
    gap_x, gap_y = 50, 80
    cols = 4

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mxGraphModel><root>',
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
    ]

    node_cell: dict[str, int] = {}
    for i, (nid, label) in enumerate(nodes.items()):
        col = i % cols
        row = i // cols
        x = col * (cell_w + gap_x) + 40
        y = row * (cell_h + gap_y) + 40
        cnum = i + 2
        node_cell[nid] = cnum
        style = "shape=table;" if is_er else "rounded=1;whiteSpace=wrap;html=1;"
        safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        xml_parts.append(
            f'<mxCell id="{cnum}" value="{safe_label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" as="geometry"/></mxCell>'
        )

    for i, (src, tgt, lbl) in enumerate(edges):
        s = node_cell.get(src)
        t = node_cell.get(tgt)
        if s and t:
            cnum = len(nodes) + 2 + i
            safe_lbl = lbl.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml_parts.append(
                f'<mxCell id="{cnum}" value="{safe_lbl}" edge="1" source="{s}" target="{t}" parent="1">'
                f'<mxGeometry relative="1" as="geometry"/></mxCell>'
            )

    xml_parts.append("</root></mxGraphModel>")
    return "\n".join(xml_parts)
