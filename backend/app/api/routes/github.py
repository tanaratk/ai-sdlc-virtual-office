"""GitHub Integration API -- /projects/{project_id}/github/..."""
import os
import re
import uuid
from datetime import UTC, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Document, DocumentType, GitHubIssue, GitHubSetting, Project
from app.services.github_service import (
    GitHubRepo,
    GitHubServiceError,
    build_issue_body,
    create_branch,
    create_issue,
    create_pull_request,
    create_repo,
    list_issues,
    parse_tasks_from_markdown,
    push_file,
    verify_connection,
)

router = APIRouter()


# โ"€โ"€ Request / Response schemas โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

class GitHubSettingUpsert(BaseModel):
    repo_owner: str = Field(min_length=1, max_length=255)
    repo_name: str = Field(min_length=1, max_length=255)
    access_token: str = Field(min_length=1)
    default_branch: str = Field(default="main", min_length=1, max_length=255)


class GitHubSettingResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    repo_owner: str
    repo_name: str
    default_branch: str
    repo_url: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GitHubVerifyResponse(BaseModel):
    ok: bool
    full_name: str
    private: bool
    html_url: str


class GitHubIssueResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    issue_number: int
    issue_url: str
    title: str
    requirement_ids: Optional[str]
    state: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateIssuesResponse(BaseModel):
    created: int
    issues: list[GitHubIssueResponse]
    skipped: int = 0
    errors: list[str] = []


class CreateBranchRequest(BaseModel):
    branch_name: str = Field(min_length=1, max_length=255)
    from_branch: Optional[str] = Field(default=None, min_length=1, max_length=255)


class CreateBranchResponse(BaseModel):
    branch: str
    sha: str


# โ"€โ"€ Helpers โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

def _get_project_or_404(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_settings_or_404(session: Session, project_id: uuid.UUID) -> GitHubSetting:
    setting = session.exec(
        select(GitHubSetting).where(GitHubSetting.project_id == project_id)
    ).first()
    if not setting:
        raise HTTPException(
            status_code=404,
            detail="GitHub settings not configured for this project. "
                   "Call PUT /github/settings first.",
        )
    return setting


def _to_repo(s: GitHubSetting) -> GitHubRepo:
    return GitHubRepo(
        owner=s.repo_owner,
        name=s.repo_name,
        token=s.access_token,
        default_branch=s.default_branch,
    )


# โ"€โ"€ Settings routes โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

@router.get(
    "/{project_id}/github/settings",
    response_model=GitHubSettingResponse,
    summary="Get GitHub settings for a project",
)
def get_github_settings(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> GitHubSettingResponse:
    _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    return GitHubSettingResponse(
        id=str(s.id),
        project_id=str(s.project_id),
        repo_owner=s.repo_owner,
        repo_name=s.repo_name,
        default_branch=s.default_branch,
        repo_url=f"https://github.com/{s.repo_owner}/{s.repo_name}",
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.put(
    "/{project_id}/github/settings",
    response_model=GitHubSettingResponse,
    summary="Save (or update) GitHub settings and verify connection",
)
def upsert_github_settings(
    project_id: uuid.UUID,
    body: GitHubSettingUpsert,
    session: Annotated[Session, Depends(get_session)],
) -> GitHubSettingResponse:
    _get_project_or_404(session, project_id)

    # Verify access before saving
    repo = GitHubRepo(
        owner=body.repo_owner,
        name=body.repo_name,
        token=body.access_token,
        default_branch=body.default_branch,
    )
    try:
        info = verify_connection(repo)
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    existing = session.exec(
        select(GitHubSetting).where(GitHubSetting.project_id == project_id)
    ).first()

    now = datetime.now(UTC)
    if existing:
        existing.repo_owner = body.repo_owner
        existing.repo_name = body.repo_name
        existing.access_token = body.access_token
        existing.default_branch = info.get("default_branch", body.default_branch)
        existing.updated_at = now
        session.commit()
        session.refresh(existing)
        s = existing
    else:
        s = GitHubSetting(
            project_id=project_id,
            repo_owner=body.repo_owner,
            repo_name=body.repo_name,
            access_token=body.access_token,
            default_branch=info.get("default_branch", body.default_branch),
        )
        session.add(s)
        session.commit()
        session.refresh(s)

    return GitHubSettingResponse(
        id=str(s.id),
        project_id=str(s.project_id),
        repo_owner=s.repo_owner,
        repo_name=s.repo_name,
        default_branch=s.default_branch,
        repo_url=f"https://github.com/{s.repo_owner}/{s.repo_name}",
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.post(
    "/{project_id}/github/verify",
    response_model=GitHubVerifyResponse,
    summary="Verify GitHub connection for a project",
)
def verify_github(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> GitHubVerifyResponse:
    _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    try:
        info = verify_connection(_to_repo(s))
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return GitHubVerifyResponse(
        ok=True,
        full_name=info["full_name"],
        private=info["private"],
        html_url=info["html_url"],
    )


# โ"€โ"€ Issues routes โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

@router.get(
    "/{project_id}/github/issues",
    response_model=list[GitHubIssueResponse],
    summary="List GitHub issues created from this project",
)
def list_github_issues(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> list[GitHubIssueResponse]:
    _get_project_or_404(session, project_id)
    issues = session.exec(
        select(GitHubIssue)
        .where(GitHubIssue.project_id == project_id)
        .order_by(GitHubIssue.created_at.desc())
    ).all()
    return [
        GitHubIssueResponse(
            id=str(i.id),
            project_id=str(i.project_id),
            issue_number=i.issue_number,
            issue_url=i.issue_url,
            title=i.title,
            requirement_ids=i.requirement_ids,
            state=i.state,
            created_at=i.created_at,
        )
        for i in issues
    ]


@router.post(
    "/{project_id}/github/issues",
    response_model=CreateIssuesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create GitHub issues from the project's code task list",
)
def create_github_issues(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> CreateIssuesResponse:
    project = _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    repo = _to_repo(s)

    # Load the latest code_task_list document
    task_doc = session.exec(
        select(Document).where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.code_task_list,
        ).order_by(Document.created_at.desc())
    ).first()
    if not task_doc:
        raise HTTPException(
            status_code=404,
            detail="No code task list document found for this project. "
                   "Run the Developer Agent first.",
        )

    tasks = parse_tasks_from_markdown(task_doc.content_markdown)
    created_issues: list[GitHubIssueResponse] = []
    errors: list[str] = []
    skipped = 0

    for task in tasks:
        # Skip if issue with same title already exists in DB
        existing = session.exec(
            select(GitHubIssue).where(
                GitHubIssue.project_id == project_id,
                GitHubIssue.title == task.title,
            )
        ).first()
        if existing:
            skipped += 1
            continue

        try:
            result = create_issue(
                repo=repo,
                title=task.title,
                body=build_issue_body(task, project.name),
                labels=["ai-sdlc", "needs-review"],
            )
        except GitHubServiceError as exc:
            errors.append(f"'{task.title}': {exc}")
            continue

        gh_issue = GitHubIssue(
            project_id=project_id,
            issue_number=result["number"],
            issue_url=result["url"],
            title=result["title"],
            requirement_ids=", ".join(task.requirement_ids) if task.requirement_ids else None,
            state=result["state"],
        )
        session.add(gh_issue)
        session.flush()  # get id before commit

        created_issues.append(GitHubIssueResponse(
            id=str(gh_issue.id),
            project_id=str(gh_issue.project_id),
            issue_number=gh_issue.issue_number,
            issue_url=gh_issue.issue_url,
            title=gh_issue.title,
            requirement_ids=gh_issue.requirement_ids,
            state=gh_issue.state,
            created_at=gh_issue.created_at,
        ))

    session.commit()
    return CreateIssuesResponse(
        created=len(created_issues),
        issues=created_issues,
        skipped=skipped,
        errors=errors,
    )


# โ"€โ"€ Branch route โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€โ"€

@router.post(
    "/{project_id}/github/branches",
    response_model=CreateBranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a branch in the connected GitHub repository",
)
def create_github_branch(
    project_id: uuid.UUID,
    body: CreateBranchRequest,
    session: Annotated[Session, Depends(get_session)],
) -> CreateBranchResponse:
    _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    try:
        result = create_branch(repo=_to_repo(s), branch_name=body.branch_name,
                               from_branch=body.from_branch)
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CreateBranchResponse(**result)


# ── Push Generated Application to a new GitHub repo ──────────────────────────

class PushAppRequest(BaseModel):
    repo_name: Optional[str] = None   # defaults to {project_name}-app
    private: bool = False


class PushAppResponse(BaseModel):
    repo_url: str
    repo_full_name: str
    files_pushed: int
    errors: list[str]


def _resolve_generated_dir(project: Project) -> str:
    raw = project.workspace_path or "/workspace"
    container_path = re.sub(
        r"^[A-Za-z]:[/\\]workspace", "/workspace", raw, flags=re.IGNORECASE
    )
    if not container_path.startswith("/workspace"):
        container_path = "/workspace"
    safe_name = re.sub(r"[^\w\-]", "_", project.name or "project")
    return os.path.join(container_path, safe_name, "generated_app")


def _safe_repo_name(name: str) -> str:
    slug = re.sub(r"[^\w\-.]", "-", name).strip("-").lower()
    return f"{slug or 'project'}-app"


@router.post(
    "/{project_id}/github/push-app",
    response_model=PushAppResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new GitHub repo and push the generated application files",
)
def push_generated_app(
    project_id: uuid.UUID,
    body: PushAppRequest,
    session: Annotated[Session, Depends(get_session)],
) -> PushAppResponse:
    project = _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)

    gen_dir = _resolve_generated_dir(project)
    if not os.path.isdir(gen_dir):
        raise HTTPException(
            status_code=404,
            detail="No generated code found. Run the Developer Agent pipeline step first.",
        )

    repo_name = body.repo_name or _safe_repo_name(project.name or "project")

    # Create the new repo
    try:
        repo_info = create_repo(
            token=s.access_token,
            repo_name=repo_name,
            description=f"Generated by AI-SDLC Working Office — {project.name}",
            private=body.private,
        )
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    push_repo = GitHubRepo(
        owner=s.repo_owner,
        name=repo_name,
        token=s.access_token,
    )

    # Collect and push all files
    errors: list[str] = []
    pushed = 0

    for root, _dirs, files in os.walk(gen_dir):
        for fname in sorted(files):
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, gen_dir).replace("\\", "/")
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
                push_file(
                    repo=push_repo,
                    path=rel_path,
                    content_bytes=content,
                    commit_message=f"feat: add {rel_path}",
                )
                pushed += 1
            except (GitHubServiceError, OSError) as exc:
                errors.append(f"{rel_path}: {exc}")

    return PushAppResponse(
        repo_url=repo_info["html_url"],
        repo_full_name=repo_info["full_name"],
        files_pushed=pushed,
        errors=errors,
    )


# ── Create Pull Request ───────────────────────────────────────────────────────

class CreatePRRequest(BaseModel):
    head:  str = Field(min_length=1, max_length=255, description="Branch with changes")
    title: str = Field(min_length=1, max_length=500)
    body:  str = Field(default="")


class CreatePRResponse(BaseModel):
    number: int
    url:    str
    title:  str


@router.post(
    "/{project_id}/github/pull-request",
    response_model=CreatePRResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a GitHub pull request from a branch to the project's default branch",
)
def create_github_pr(
    project_id: uuid.UUID,
    body: CreatePRRequest,
    session: Annotated[Session, Depends(get_session)],
) -> CreatePRResponse:
    _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    repo = _to_repo(s)
    try:
        result = create_pull_request(
            repo=repo,
            head=body.head,
            base=repo.default_branch,
            title=body.title,
            body=body.body,
        )
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CreatePRResponse(**result)


# ── Push SDLC Docs → branch → PR ─────────────────────────────────────────────

_DOC_TYPE_FILENAME: dict[str, str] = {
    "requirement_summary": "01-requirement-summary.md",
    "gap_analysis_report": "02-gap-analysis-report.md",
    "brd":                 "03-brd.md",
    "fsd":                 "04-fsd.md",
    "user_story":          "05-user-stories.md",
    "architecture_design": "06-architecture-design.md",
    "database_design":     "07-database-design.md",
    "api_spec":            "08-api-spec.md",
    "screen_spec":         "09-screen-spec.md",
    "test_case":           "10-test-cases.md",
    "code_task_list":      "11-code-task-list.md",
    "technical_design":    "12-technical-design.md",
    "change_impact_report":"13-change-impact-report.md",
    "documentation":       "14-documentation.md",
    "pm_report":           "15-pm-report.md",
}


class PushDocsResponse(BaseModel):
    branch:       str
    pr_url:       str
    pr_number:    int
    files_pushed: int


@router.post(
    "/{project_id}/github/push-docs",
    response_model=PushDocsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Push all AI-generated SDLC documents to a new branch and open a PR",
)
def push_docs_to_github(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> PushDocsResponse:
    project = _get_project_or_404(session, project_id)
    s = _get_settings_or_404(session, project_id)
    repo = _to_repo(s)

    # Load latest version of each document type
    docs = session.exec(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    ).all()

    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No documents found for this project. Run the pipeline first.",
        )

    # Keep only the latest per document_type
    seen: set[str] = set()
    unique_docs: list[Document] = []
    for doc in docs:
        dtype = doc.document_type if isinstance(doc.document_type, str) else doc.document_type.value
        if dtype not in seen:
            seen.add(dtype)
            unique_docs.append(doc)

    # Create branch ai-sdlc/docs-{YYYYMMDD-HHMMSS}
    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    branch_name = f"ai-sdlc/docs-{ts}"
    try:
        create_branch(repo=repo, branch_name=branch_name)
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=f"Branch creation failed: {exc}")

    # Push each document under docs/ai-sdlc/
    pushed = 0
    doc_branch_repo = GitHubRepo(
        owner=repo.owner,
        name=repo.name,
        token=repo.token,
        default_branch=branch_name,
    )
    for doc in unique_docs:
        dtype = doc.document_type if isinstance(doc.document_type, str) else doc.document_type.value
        filename = _DOC_TYPE_FILENAME.get(dtype, f"{dtype}.md")
        path = f"docs/ai-sdlc/{filename}"
        content = (doc.content_markdown or "").encode("utf-8")
        try:
            push_file(
                repo=doc_branch_repo,
                path=path,
                content_bytes=content,
                commit_message=f"docs(ai-sdlc): add {filename}",
            )
            pushed += 1
        except GitHubServiceError:
            pass  # continue pushing other docs

    # Create PR from the docs branch to default
    project_name = project.name or "Project"
    safe_name = re.sub(r"[^\w\-]", "_", project_name)
    pr_title = f"docs(ai-sdlc): SDLC documents for {project_name} [{ts}]"
    pr_body = (
        f"## AI-SDLC Working Office — Generated Documents\n\n"
        f"**Project:** {project_name}  \n"
        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}  \n"
        f"**Documents pushed:** {pushed}\n\n"
        f"This PR was created automatically by AI-SDLC Working Office.\n\n"
        f"### Included Documents\n\n"
        + "\n".join(
            f"- `docs/ai-sdlc/{_DOC_TYPE_FILENAME.get(doc.document_type if isinstance(doc.document_type, str) else doc.document_type.value, 'unknown.md')}`"
            for doc in unique_docs
        )
        + "\n\n---\n_Review these documents before merging._"
    )

    try:
        pr = create_pull_request(
            repo=repo,
            head=branch_name,
            base=repo.default_branch,
            title=pr_title,
            body=pr_body,
        )
    except GitHubServiceError as exc:
        raise HTTPException(status_code=400, detail=f"PR creation failed: {exc}")

    return PushDocsResponse(
        branch=branch_name,
        pr_url=pr["url"],
        pr_number=pr["number"],
        files_pushed=pushed,
    )
