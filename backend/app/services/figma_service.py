"""Figma REST API service — read file info and push screen spec annotations as comments."""
import re
from dataclasses import dataclass, field

import httpx

_BASE = "https://api.figma.com/v1"
_TIMEOUT = 15.0


class FigmaServiceError(Exception):
    pass


def _headers(token: str) -> dict[str, str]:
    return {"X-Figma-Token": token}


# ── File key extraction ───────────────────────────────────────────────────────

def extract_file_key(url_or_key: str) -> str:
    """Extract the file key from a Figma URL or return as-is if it's already a key."""
    # Figma URLs: https://www.figma.com/file/{key}/... or /design/{key}/...
    m = re.search(r"figma\.com/(?:file|design|proto)/([A-Za-z0-9_-]+)", url_or_key)
    if m:
        return m.group(1)
    # Assume it's already a raw key
    cleaned = url_or_key.strip().rstrip("/")
    if re.match(r"^[A-Za-z0-9_-]+$", cleaned):
        return cleaned
    raise FigmaServiceError(
        "Could not extract a Figma file key from the provided URL. "
        "Please paste the full Figma file URL."
    )


# ── API calls ─────────────────────────────────────────────────────────────────

def get_file_info(file_key: str, token: str) -> dict:
    """Return {name, pages} or raise FigmaServiceError."""
    url = f"{_BASE}/files/{file_key}?depth=1"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, headers=_headers(token))
    if resp.status_code == 403:
        raise FigmaServiceError("Invalid Figma token or insufficient permissions.")
    if resp.status_code == 404:
        raise FigmaServiceError(f"Figma file '{file_key}' not found.")
    if not resp.is_success:
        raise FigmaServiceError(f"Figma API error {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    pages = [p["name"] for p in data.get("document", {}).get("children", [])]
    return {"name": data.get("name", ""), "pages": pages}


def get_design_detail(file_key: str, token: str, node_id: str | None = None) -> dict:
    """
    Fetch design info from a Figma file.
    Returns file name, key, pages. If node_id given, also returns node details.
    """
    info = get_file_info(file_key, token)
    result: dict = {
        "file_name": info["name"],
        "file_key": file_key,
        "file_url": f"https://www.figma.com/file/{file_key}",
        "pages": info["pages"],
        "page_count": len(info["pages"]),
    }
    if node_id:
        result["node"] = get_node(file_key, node_id, token)
    return result


def get_node(file_key: str, node_id: str, token: str) -> dict:
    """Fetch a specific node from a Figma file and return its details."""
    url = f"{_BASE}/files/{file_key}/nodes?ids={node_id}"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, headers=_headers(token))
    if resp.status_code == 403:
        raise FigmaServiceError("Invalid Figma token or insufficient permissions.")
    if resp.status_code == 404:
        raise FigmaServiceError(f"Node '{node_id}' not found in Figma file '{file_key}'.")
    if not resp.is_success:
        raise FigmaServiceError(f"Figma API error {resp.status_code}: {resp.text[:200]}")
    nodes = resp.json().get("nodes", {})
    entry = nodes.get(node_id, {})
    doc = entry.get("document", {})
    children = doc.get("children", [])
    return {
        "id": doc.get("id", node_id),
        "name": doc.get("name", ""),
        "type": doc.get("type", ""),
        "child_count": len(children),
        "children": [
            {"id": c.get("id"), "name": c.get("name"), "type": c.get("type")}
            for c in children[:20]  # cap to 20 children
        ],
    }


def push_comment(file_key: str, token: str, message: str) -> dict:
    """Post a root-level comment on a Figma file."""
    url = f"{_BASE}/files/{file_key}/comments"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.post(url, headers=_headers(token), json={"message": message})
    if not resp.is_success:
        raise FigmaServiceError(f"Failed to post comment: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    return {"id": data.get("id", ""), "message": message}


# ── Screen spec parser ────────────────────────────────────────────────────────

@dataclass
class ParsedScreen:
    screen_id: str          # e.g. UI-001
    name: str               # e.g. Dashboard
    description: str = ""
    body: str = ""          # full section markdown
    components: list[str] = field(default_factory=list)


def parse_screens_from_spec(markdown: str) -> list[ParsedScreen]:
    """
    Parse the UX Agent's screen_spec document into individual screens.
    Looks for sections with an ID pattern like UI-001 or ## Screen Name.
    """
    screens: list[ParsedScreen] = []

    # Split on ## headings
    sections = re.split(r"\n(?=## )", "\n" + markdown)

    for section in sections:
        lines = section.strip().splitlines()
        if not lines:
            continue
        header = lines[0].lstrip("#").strip()

        # Try to extract UI-XXX id from header
        id_match = re.search(r"(UI-\d{3})", header, re.IGNORECASE)
        screen_id = id_match.group(1).upper() if id_match else ""

        # Clean name: remove the ID prefix
        name = re.sub(r"^UI-\d{3}[\s:\-–—]*", "", header, flags=re.IGNORECASE).strip()
        if not name:
            name = header

        body = "\n".join(lines[1:]).strip()
        if not body and not screen_id:
            continue

        # Skip non-screen headers
        lowered = header.lower()
        if any(k in lowered for k in ("screen inventory", "ux flow", "overview", "introduction", "summary", "table of")):
            continue

        # Extract components list
        comp_match = re.search(r"\*\*Components?\*\*:?\s*([^\n]+)", body, re.IGNORECASE)
        components = []
        if comp_match:
            raw = comp_match.group(1)
            components = [c.strip() for c in re.split(r"[,;|]", raw) if c.strip()]

        # Extract description
        desc_match = re.search(r"\*\*Description\*\*:?\s*([^\n]+)", body, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""

        screens.append(ParsedScreen(
            screen_id=screen_id or f"UI-{len(screens)+1:03d}",
            name=name,
            description=description,
            body=body[:1500],  # cap to avoid huge comments
            components=components,
        ))

    return screens


def build_comment_for_screen(screen: ParsedScreen, project_name: str) -> str:
    comp_line = f"**Components:** {', '.join(screen.components)}\n\n" if screen.components else ""
    return (
        f"🤖 AI-SDLC · {project_name} · {screen.screen_id}\n\n"
        f"**Screen:** {screen.name}\n\n"
        f"{f'**Description:** {screen.description}' + chr(10) + chr(10) if screen.description else ''}"
        f"{comp_line}"
        f"{screen.body}\n\n"
        f"---\n_Generated by UX Agent · AI-SDLC Working Office_"
    )
