"""GitHub REST API service — wraps httpx calls to api.github.com."""
import re
from dataclasses import dataclass

import httpx

_BASE = "https://api.github.com"
_TIMEOUT = 15.0


@dataclass
class GitHubRepo:
    owner: str
    name: str
    token: str
    default_branch: str = "main"

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }


class GitHubServiceError(Exception):
    pass


# ── Public functions ────────────────────────────────────────────────────────────

def verify_connection(repo: GitHubRepo) -> dict:
    """Return repo metadata or raise GitHubServiceError."""
    url = f"{_BASE}/repos/{repo.owner}/{repo.name}"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, headers=repo._headers)
    if resp.status_code == 401:
        raise GitHubServiceError("Invalid access token.")
    if resp.status_code == 404:
        raise GitHubServiceError(
            f"Repository '{repo.owner}/{repo.name}' not found or token lacks access."
        )
    if not resp.is_success:
        raise GitHubServiceError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    return {
        "full_name": data.get("full_name"),
        "private": data.get("private"),
        "default_branch": data.get("default_branch", "main"),
        "html_url": data.get("html_url"),
    }


def create_issue(
    repo: GitHubRepo,
    title: str,
    body: str,
    labels: list[str] | None = None,
) -> dict:
    """Create a GitHub issue. Returns dict with number, url, title."""
    url = f"{_BASE}/repos/{repo.owner}/{repo.name}/issues"
    payload: dict = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.post(url, headers=repo._headers, json=payload)
    if not resp.is_success:
        raise GitHubServiceError(
            f"Failed to create issue: {resp.status_code} {resp.text[:300]}"
        )
    data = resp.json()
    return {
        "number": data["number"],
        "url": data["html_url"],
        "title": data["title"],
        "state": data["state"],
    }


def create_branch(
    repo: GitHubRepo,
    branch_name: str,
    from_branch: str | None = None,
) -> dict:
    """Create a new branch from `from_branch` (defaults to repo default branch)."""
    base = from_branch or repo.default_branch

    # Get SHA of base branch
    ref_url = f"{_BASE}/repos/{repo.owner}/{repo.name}/git/ref/heads/{base}"
    with httpx.Client(timeout=_TIMEOUT) as client:
        ref_resp = client.get(ref_url, headers=repo._headers)
    if not ref_resp.is_success:
        raise GitHubServiceError(
            f"Cannot resolve base branch '{base}': {ref_resp.status_code}"
        )
    sha = ref_resp.json()["object"]["sha"]

    # Create new ref
    refs_url = f"{_BASE}/repos/{repo.owner}/{repo.name}/git/refs"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.post(
            refs_url,
            headers=repo._headers,
            json={"ref": f"refs/heads/{branch_name}", "sha": sha},
        )
    if resp.status_code == 422:
        raise GitHubServiceError(
            f"Branch '{branch_name}' already exists or name is invalid."
        )
    if not resp.is_success:
        raise GitHubServiceError(
            f"Failed to create branch: {resp.status_code} {resp.text[:300]}"
        )
    return {"branch": branch_name, "sha": sha}


def list_issues(repo: GitHubRepo, state: str = "open") -> list[dict]:
    """List issues in the repo (first page, 30 max)."""
    url = f"{_BASE}/repos/{repo.owner}/{repo.name}/issues"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(
            url,
            headers=repo._headers,
            params={"state": state, "per_page": 30},
        )
    if not resp.is_success:
        raise GitHubServiceError(f"GitHub API error {resp.status_code}")
    return [
        {
            "number": i["number"],
            "title": i["title"],
            "url": i["html_url"],
            "state": i["state"],
            "labels": [lb["name"] for lb in i.get("labels", [])],
        }
        for i in resp.json()
        if "pull_request" not in i  # exclude PRs
    ]


# ── Markdown task parser ────────────────────────────────────────────────────────

@dataclass
class ParsedTask:
    title: str
    body: str
    requirement_ids: list[str]


def parse_tasks_from_markdown(markdown: str) -> list[ParsedTask]:
    """Extract individual tasks from a code_task_list markdown document.

    Looks for sections that start with ## (task headers). Falls back to
    returning a single task with the whole document as body.
    """
    # Split on ## headings (task sections)
    sections = re.split(r"\n(?=## )", markdown)
    tasks: list[ParsedTask] = []

    for section in sections:
        lines = section.strip().splitlines()
        if not lines:
            continue
        header = lines[0].lstrip("#").strip()
        # Skip non-task headers (table of contents, intro sections)
        if not header or header.lower().startswith(("task list", "code task", "overview", "summary")):
            continue

        body = "\n".join(lines[1:]).strip()
        # Extract requirement IDs mentioned in the section
        req_ids = re.findall(r"\b(?:FR|NFR|BR|US)-\d{3}\b", section)
        req_ids = list(dict.fromkeys(req_ids))  # deduplicate, preserve order

        tasks.append(ParsedTask(title=header, body=body, requirement_ids=req_ids))

    if not tasks:
        # Fallback: whole document as one issue
        first_line = markdown.splitlines()[0].lstrip("#").strip() if markdown else "Code Task List"
        req_ids = re.findall(r"\b(?:FR|NFR|BR|US)-\d{3}\b", markdown)
        tasks.append(ParsedTask(
            title=first_line,
            body=markdown[:3000],
            requirement_ids=list(dict.fromkeys(req_ids)),
        ))

    return tasks


def build_issue_body(task: ParsedTask, project_name: str) -> str:
    req_line = (
        f"**Linked Requirements:** {', '.join(task.requirement_ids)}\n\n"
        if task.requirement_ids
        else ""
    )
    return (
        f"<!-- Generated by AI-SDLC Working Office -->\n\n"
        f"**Project:** {project_name}\n\n"
        f"{req_line}"
        f"{task.body}\n\n"
        f"---\n_Created by Developer Agent. Human review required before implementation._"
    )
