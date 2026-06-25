"""DevOps Agent -- Sprint 35.

Generates deployment files, runs Docker build/deploy checks when Docker is
available, performs a health check, and stores both configuration and
build_report documents.
"""
import logging
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.db.models import (
    ActivityLog,
    Agent,
    AgentStatus,
    Document,
    DocumentStatus,
    DocumentType,
    EventType,
    PipelineRun,
    PipelineRunStatus,
    PipelineStep,
    PipelineStepStatus,
    Project,
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "devops-agent"
STEP_NAME = "devops_tasks"

FILE_TIMEOUT = 120.0
MIN_FILE_CHARS = 30
COMMAND_TIMEOUT = 300
HEALTH_TIMEOUT = 10


@dataclass
class CommandResult:
    name: str
    command: str
    status: str
    exit_code: int | None
    stdout: str
    stderr: str


@dataclass
class HealthResult:
    url: str
    status: str
    http_status: int | None
    detail: str


def _trunc(s: str, n: int) -> str:
    return s[:n] + "\n...(truncated)" if len(s) > n else s


def _short(s: str, n: int = 5000) -> str:
    return s if len(s) <= n else s[:n] + "\n... output truncated ..."


def _container_workspace_path(raw: str | None) -> str:
    workspace = raw or "/workspace"
    workspace = re.sub(r"^[A-Za-z]:[/\\]workspace", "/workspace", workspace, flags=re.IGNORECASE)
    if not workspace.startswith("/workspace"):
        workspace = "/workspace"
    return workspace


def _safe_name(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name)


_DEVOPS_FILES_DEFAULT: list[tuple[str, str, str]] = [
    ("Dockerfile.backend",         "dockerfile", "backend_docker"),
    ("Dockerfile.frontend",        "dockerfile", "frontend_docker"),
    ("docker-compose.yml",         "yaml",       "compose_dev"),
    ("docker-compose.prod.yml",    "yaml",       "compose_prod"),
    ("nginx.conf",                 "text",       "nginx"),
    (".env.example",               "bash",       "env_example"),
    (".github/workflows/ci.yml",   "yaml",       "github_ci"),
    ("README.md",                  "markdown",   "readme"),
]

_DEVOPS_FILES_DOTNET: list[tuple[str, str, str]] = [
    # .NET projects: single app Dockerfile (no separate frontend container)
    ("Dockerfile",                 "dockerfile", "backend_docker"),
    ("docker-compose.yml",         "yaml",       "compose_dev"),
    ("docker-compose.prod.yml",    "yaml",       "compose_prod"),
    (".env",                       "bash",       "env_defaults"),
    (".env.example",               "bash",       "env_example"),
    (".github/workflows/ci.yml",   "yaml",       "github_ci"),
    ("README.md",                  "markdown",   "readme"),
]

_DEVOPS_FILES_DOTNET_WEBFORMS: list[tuple[str, str, str]] = [
    # Web Forms on .NET Framework: requires Windows Server Core container
    ("Dockerfile",                 "dockerfile", "backend_docker"),
    ("docker-compose.yml",         "yaml",       "compose_dev"),
    (".env",                       "bash",       "env_defaults"),
    (".env.example",               "bash",       "env_example"),
    (".github/workflows/ci.yml",   "yaml",       "github_ci"),
    ("README.md",                  "markdown",   "readme"),
]

_DEVOPS_FILES_NODE: list[tuple[str, str, str]] = [
    # Node.js projects: separate backend + frontend containers
    ("Dockerfile.backend",         "dockerfile", "backend_docker"),
    ("Dockerfile.frontend",        "dockerfile", "frontend_docker"),
    ("docker-compose.yml",         "yaml",       "compose_dev"),
    ("docker-compose.prod.yml",    "yaml",       "compose_prod"),
    ("nginx.conf",                 "text",       "nginx"),
    (".env.example",               "bash",       "env_example"),
    (".github/workflows/ci.yml",   "yaml",       "github_ci"),
    ("README.md",                  "markdown",   "readme"),
]

_PURPOSES_DEFAULT: dict[str, str] = {
    "backend_docker": "Multi-stage Dockerfile for FastAPI (Python) backend using python:3.11-slim",
    "frontend_docker": "Multi-stage Dockerfile for React/Vite frontend using node:20-alpine build stage and nginx:alpine serve stage",
    "compose_dev": "docker-compose.yml for local build and deployment with backend, frontend, and db services",
    "compose_prod": "docker-compose.prod.yml for production-like deployment",
    "nginx": "nginx reverse proxy config: route /api/ to backend, / to frontend static files",
    "env_example": "Environment variable template with DATABASE_URL, SECRET_KEY, JWT_SECRET, CORS_ORIGINS",
    "github_ci": "GitHub Actions CI workflow for Python/Node.js: install deps, lint, test, build Docker images",
    "readme": "Runbook with Docker build/deploy commands",
}

_PURPOSES_NODE: dict[str, str] = {
    "backend_docker": "Multi-stage Dockerfile for Node.js/Express backend using node:20-alpine. Build: npm ci. Runtime: node src/index.js or npm start on port 3000.",
    "frontend_docker": "Multi-stage Dockerfile for React/Vue/Angular frontend using node:20-alpine build stage (npm run build) and nginx:alpine serve stage.",
    "compose_dev": "docker-compose.yml with THREE services: 'backend' (Node.js), 'frontend' (built static via nginx), 'db' (postgres:16). Include healthcheck on db service. frontend depends_on backend.",
    "compose_prod": "docker-compose.prod.yml for production Node.js app deployment",
    "nginx": "nginx reverse proxy config: route /api/ to backend:3000, / to frontend static files",
    "env_example": "Environment variable template: DATABASE_URL, PORT=3000, JWT_SECRET, NODE_ENV",
    "github_ci": "GitHub Actions CI workflow for Node.js: actions/setup-node, npm ci, npm test, npm run build, docker build",
    "readme": "Runbook with Docker build/deploy commands for Node.js app",
}

_PURPOSES_DOTNET_WEBFORMS: dict[str, str] = {
    "backend_docker": "Dockerfile for ASP.NET Web Forms on .NET Framework using mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2022 build stage and mcr.microsoft.com/dotnet/framework/aspnet:4.8-windowsservercore-ltsc2022 runtime stage. MSBuild build command. ENTRYPOINT must start IIS.",
    "compose_dev": "docker-compose.yml with TWO services: 'app' (Windows container, ASP.NET Web Forms) and 'db' (mcr.microsoft.com/mssql/server:2022-latest). Note: Windows containers cannot run Linux db images — use SQL Server.",
    "env_defaults": "Actual .env file with real default values: DB_SERVER=db, DB_NAME matching project, DB_USER=sa, DB_PASSWORD=YourStrong!Passw0rd",
    "env_example": ".env.example with placeholder values for ASP.NET Web Forms app connecting to SQL Server",
    "github_ci": "GitHub Actions CI workflow for .NET Framework using actions/setup-dotnet with framework 4.x, MSBuild restore and build, NuGet restore",
    "readme": "Runbook for ASP.NET Web Forms Docker deployment. Note: requires Windows Docker daemon.",
}

_PURPOSES_DOTNET: dict[str, str] = {
    "backend_docker": "Multi-stage Dockerfile for ASP.NET Core application using mcr.microsoft.com/dotnet/sdk:8.0 build stage and mcr.microsoft.com/dotnet/aspnet:8.0 runtime stage. Run: dotnet publish -c Release -o /app/publish. ENTRYPOINT dotnet App.dll on port 80.",
    "compose_dev": "docker-compose.yml with TWO services only: 'app' (ASP.NET Core, builds from Dockerfile, port 80) and 'db' (postgres:16). The 'db' service MUST have a healthcheck (pg_isready). The 'app' service MUST have depends_on: db: condition: service_healthy. Pass DB_HOST, DB_NAME, DB_USER, DB_PASSWORD as environment from .env file.",
    "compose_prod": "docker-compose.prod.yml for production-like deployment of the ASP.NET Core app",
    "env_defaults": "Actual .env file (not example) with real default values safe for local development: DB_USER=postgres, DB_PASSWORD=devpassword123, DB_NAME matching the project name, DB_HOST=db",
    "env_example": ".env.example showing required environment variables with placeholder values for ASP.NET Core app",
    "github_ci": "GitHub Actions CI workflow for .NET using actions/setup-dotnet, dotnet restore, dotnet build, dotnet test, dotnet publish",
    "readme": "Runbook with Docker build/deploy commands for .NET app including how to run locally with docker compose up",
}


def _detect_stack_type(tech_stack: dict | None) -> str:
    if not tech_stack:
        return "python"
    backend = (tech_stack.get("backend") or "").lower()
    frontend = (tech_stack.get("frontend") or "").lower()
    container = (tech_stack.get("container") or "").lower()
    if any(k in backend or k in frontend for k in [".net", "asp.net", "aspnet", "blazor", "razor"]):
        # Web Forms on .NET Framework needs Windows containers
        if "web forms" in backend or "web forms" in frontend or "windows" in container:
            return "dotnet_webforms"
        return "dotnet"
    if any(k in backend for k in ["node", "express", "nest", "javascript", "typescript"]):
        return "node"
    return "python"


def _devops_files_for_stack(tech_stack: dict | None) -> list[tuple[str, str, str]]:
    t = _detect_stack_type(tech_stack)
    if t == "dotnet":
        return _DEVOPS_FILES_DOTNET
    if t == "dotnet_webforms":
        return _DEVOPS_FILES_DOTNET_WEBFORMS
    if t == "node":
        return _DEVOPS_FILES_NODE
    return _DEVOPS_FILES_DEFAULT


def _purposes_for_stack(tech_stack: dict | None) -> dict[str, str]:
    t = _detect_stack_type(tech_stack)
    if t == "dotnet":
        return _PURPOSES_DOTNET
    if t == "dotnet_webforms":
        return _PURPOSES_DOTNET_WEBFORMS
    if t == "node":
        return _PURPOSES_NODE
    return _PURPOSES_DEFAULT


def _tech_stack_description(tech_stack: dict | None) -> str:
    if not tech_stack:
        return "FastAPI (Python 3.11) + PostgreSQL 15 for backend; React + Vite + Node 20 for frontend."
    parts = []
    for key, label in [
        ("backend", "Backend"), ("backend_version", "Backend version"),
        ("frontend", "Frontend"), ("frontend_version", "Frontend version"),
        ("database", "Database"), ("database_version", "Database version"),
        ("language", "Language"), ("orm", "ORM"), ("auth", "Auth"),
        ("cloud", "Cloud"), ("container", "Container"), ("testing", "Testing"),
    ]:
        if tech_stack.get(key):
            parts.append(f"{label}: {tech_stack[key]}")
    return "; ".join(parts) + "." if parts else "FastAPI + React + PostgreSQL."


_SYSTEM_PROMPT = """\
You are an expert DevOps engineer and infrastructure specialist.
You write clean deployment configuration files for full-stack web applications.

PROJECT TECH STACK: {tech_stack_info}

Rules:
- Output ONLY the file content. No markdown fences. No explanation.
- Match all Dockerfile, CI, and config to the PROJECT TECH STACK above.
- For .NET/ASP.NET Core MVC or Razor Pages:
    * Dockerfile: multi-stage using mcr.microsoft.com/dotnet/sdk:8.0 → mcr.microsoft.com/dotnet/aspnet:8.0
    * Build: dotnet restore → dotnet publish "App.csproj" -c Release -o /app/publish
    * Runtime ENTRYPOINT: ["dotnet", "App.dll"]
    * docker-compose.yml: exactly TWO services (app + db). NO nginx, NO redis unless explicitly required.
    * The 'db' postgres service MUST include a healthcheck:
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U $${DB_USER} -d $${DB_NAME}"]
          interval: 5s
          timeout: 5s
          retries: 10
    * The 'app' service MUST use depends_on: db: condition: service_healthy
    * The 'app' service MUST load env_file: .env
    * The .env file MUST contain actual working default values (not placeholders):
        DB_USER=postgres
        DB_PASSWORD=devpassword123
        DB_NAME=<project_name_db>
        DB_HOST=db
- For Node.js / Express: use node:20-alpine image, npm ci, npm start commands. Separate backend and frontend containers.
- For Python / FastAPI: use python:3.11-slim image, pip install, uvicorn commands. Include redis if Celery is in the stack.
- For ASP.NET Web Forms on .NET Framework: use mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2022 build stage and mcr.microsoft.com/dotnet/framework/aspnet:4.8-windowsservercore-ltsc2022 runtime stage. MSBuild for build, not dotnet. Windows containers do not support Linux-based postgres — use mcr.microsoft.com/mssql/server:2022-latest for SQL Server instead.
- Use multi-stage Docker builds for all stacks.
- .env.example must list required environment variables with placeholder values.
- GitHub Actions CI must use the correct language toolchain for the stack:
    * .NET Core: actions/setup-dotnet, dotnet restore, dotnet build, dotnet test, dotnet publish
    * .NET Framework (Web Forms): MSBuild with NuGet restore
    * Node.js: actions/setup-node@v4 with node-version: '20', npm ci, npm test, npm run build
    * Python: actions/setup-python, pip install, pytest
- Cloud-specific deployment:
    * If cloud is Azure: include azure/login action, push to Azure Container Registry (ACR), deploy to Azure App Service or AKS
    * If cloud is AWS: include aws-actions/configure-aws-credentials, push to ECR, deploy to ECS/Fargate
    * If cloud is not specified: use generic docker build/push to ghcr.io
- Never hardcode real passwords in .env.example — use placeholders like CHANGE_ME.
- In .env (non-example), use safe local dev defaults.
"""

_FILE_TEMPLATE = """\
Generate the complete content of this file:

FILE: {path}
FORMAT: {lang}
PURPOSE: {purpose}

RELEVANT CONTEXT:
{context}

Output the file content directly. No fences, no explanation.
"""

def _render_config_summary(results: list[tuple[str, bool]], project_id: str, doc_id: str) -> str:
    ok = sum(1 for _, success in results if success)
    fail = len(results) - ok
    rows = "\n".join(f"| `{path}` | {'OK' if success else 'FAILED'} |" for path, success in results)
    return f"""# DevOps Configuration Summary

**Project ID:** `{project_id}`  
**Document ID:** `{doc_id}`  
**Generated By:** DevOps Agent  
**Pipeline Step:** 10 of 12  
**Status:** Draft -- Awaiting Review

## Generation Results

| Files OK | Files Failed |
|---:|---:|
| {ok} | {fail} |

## Files Generated

| Path | Status |
|---|---|
{rows}

## Output Location

Files are written to `generated_app/` inside the project workspace.
"""


def _render_build_report(
    project_id: uuid.UUID,
    doc_id: uuid.UUID,
    app_dir: Path,
    command_results: list[CommandResult],
    health: HealthResult,
    rollback: CommandResult | None,
) -> str:
    failed = sum(1 for r in command_results if r.status == "failed")
    skipped = sum(1 for r in command_results if r.status == "skipped")
    passed = sum(1 for r in command_results if r.status == "passed")
    overall = "PASS" if failed == 0 and health.status == "passed" else "FAIL"
    if skipped and failed == 0 and health.status != "failed":
        overall = "PARTIAL"

    result_rows = "\n".join(
        f"| {r.name} | `{r.command}` | {r.status.upper()} | {r.exit_code if r.exit_code is not None else '-'} |"
        for r in command_results
    )
    output_blocks = "\n".join(
        f"""### {r.name}

**Command:** `{r.command}`  
**Status:** {r.status.upper()}  
**Exit code:** {r.exit_code if r.exit_code is not None else "-"}

```text
STDOUT:
{_short(r.stdout)}

STDERR:
{_short(r.stderr)}
```
"""
        for r in command_results
    )
    rollback_block = ""
    if rollback:
        rollback_block = f"""## Rollback

**Command:** `{rollback.command}`  
**Status:** {rollback.status.upper()}  
**Exit code:** {rollback.exit_code if rollback.exit_code is not None else "-"}

```text
STDOUT:
{_short(rollback.stdout)}

STDERR:
{_short(rollback.stderr)}
```
"""

    return f"""# Build Report

**Project ID:** `{project_id}`  
**Document ID:** `{doc_id}`  
**Generated By:** DevOps Agent  
**Pipeline Step:** 10 of 12  
**Generated At:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}  
**Overall Status:** {overall}

## Summary

| Metric | Count |
|---|---:|
| Commands passed | {passed} |
| Commands failed | {failed} |
| Commands skipped | {skipped} |

**Workspace:** `{app_dir}`

## Command Results

| Stage | Command | Status | Exit Code |
|---|---|---|---:|
{result_rows}

## Health Check

| URL | Status | HTTP Status | Detail |
|---|---|---:|---|
| `{health.url}` | {health.status.upper()} | {health.http_status if health.http_status is not None else '-'} | {health.detail} |

## Runner Output

{output_blocks}

{rollback_block}
"""


class DevOpsAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None

        try:
            run = self._get_run(run_id)
            if run.status == PipelineRunStatus.failed:
                logger.info("DevOpsAgent skipped -- run %s already failed", run_id)
                return

            step = self._get_step(run_id)
            agent_row = self._get_agent_row()
            model = agent_row.model_name if agent_row else None

            run.status = PipelineRunStatus.running
            run.current_step = STEP_NAME
            step.status = PipelineStepStatus.running
            step.started_at = datetime.now(UTC)
            if agent_row:
                agent_row.status = AgentStatus.working
                agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

            arch_doc, db_doc, api_doc, fsd_doc = self._load_source_documents(run.project_id)
            project = self.session.get(Project, run.project_id)
            project_name = project.name if project else "project"
            tech_stack: dict | None = project.tech_stack if project else None
            app_dir = self._get_output_dir(run.project_id)

            docs = {
                "architecture": arch_doc.content_markdown,
                "database": db_doc.content_markdown,
                "api_spec": api_doc.content_markdown,
                "fsd": fsd_doc.content_markdown,
                "project_name": project_name,
            }

            generation_results = self._generate_devops_files(app_dir, docs, model, tech_stack)
            command_results, health, rollback = self._build_deploy_healthcheck(app_dir)

            config_doc_id = uuid.uuid4()
            config_md = _render_config_summary(generation_results, str(run.project_id), str(config_doc_id))
            config_doc = Document(
                id=config_doc_id,
                project_id=run.project_id,
                document_type=DocumentType.devops_config,
                title="DevOps Configuration Summary",
                content_markdown=config_md,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(config_doc)

            report_doc_id = uuid.uuid4()
            report_md = _render_build_report(
                project_id=run.project_id,
                doc_id=report_doc_id,
                app_dir=app_dir,
                command_results=command_results,
                health=health,
                rollback=rollback,
            )
            report_doc = Document(
                id=report_doc_id,
                project_id=run.project_id,
                document_type=DocumentType.build_report,
                title=f"Build Report -- {health.status.upper()}",
                content_markdown=report_md,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(report_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = report_doc.id
            step.completed_at = datetime.now(UTC)
            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)

            ok_files = sum(1 for _, success in generation_results if success)
            failed_commands = sum(1 for r in command_results if r.status == "failed")
            self._log_activity(
                run.project_id,
                agent_row,
                (
                    f"DevOps generated {ok_files}/{len(generation_results)} files. "
                    f"Build/deploy commands failed: {failed_commands}. "
                    f"Health check: {health.status}."
                ),
            )
            self.session.commit()

            from app.agents._workspace import write_workspace_docs

            write_workspace_docs(self.session, run.project_id, {"build_report.md": report_md})
            logger.info(
                "DevOpsAgent completed run=%s config=%s report=%s health=%s",
                run_id, config_doc_id, report_doc_id, health.status,
            )

        except Exception as exc:
            logger.exception("DevOpsAgent failed run=%s: %s", run_id, exc)
            self.session.rollback()
            try:
                run = self.session.get(PipelineRun, run_id)
                if run:
                    run.status = PipelineRunStatus.failed
                if step:
                    step.status = PipelineStepStatus.failed
                    step.error_message = str(exc)[:2000]
                    step.completed_at = datetime.now(UTC)
                if agent_row:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.now(UTC)
                self.session.commit()
            except Exception:
                logger.exception("Failed to persist DevOps failure state for run=%s", run_id)

    def _generate_devops_files(
        self,
        app_dir: Path,
        docs: dict[str, str],
        model: str | None,
        tech_stack: dict | None = None,
    ) -> list[tuple[str, bool]]:
        results: list[tuple[str, bool]] = []
        for rel_path, lang, ctx_type in _devops_files_for_stack(tech_stack):
            content = self._generate_file(rel_path, lang, ctx_type, docs, model, tech_stack)
            if content:
                self._write_file(app_dir, rel_path, content)
                results.append((rel_path, True))
            else:
                results.append((rel_path, False))
        return results

    def _build_deploy_healthcheck(
        self,
        app_dir: Path,
    ) -> tuple[list[CommandResult], HealthResult, CommandResult | None]:
        docker = shutil.which("docker")
        if not docker:
            return (
                [CommandResult(
                    name="docker",
                    command="docker --version",
                    status="skipped",
                    exit_code=None,
                    stdout="Docker CLI is not available in this runtime.",
                    stderr="",
                )],
                HealthResult(url="-", status="skipped", http_status=None, detail="Health check skipped because Docker is unavailable."),
                None,
            )

        compose_file = app_dir / "docker-compose.yml"
        if not compose_file.exists():
            return (
                [CommandResult(
                    name="compose-config",
                    command="docker compose -f docker-compose.yml config",
                    status="failed",
                    exit_code=None,
                    stdout="",
                    stderr=f"Missing compose file: {compose_file}",
                )],
                HealthResult(url="-", status="failed", http_status=None, detail="Missing docker-compose.yml."),
                None,
            )

        results = [
            self._run_command("compose-config", [docker, "compose", "-f", str(compose_file), "config"], app_dir),
            self._run_command("compose-build", [docker, "compose", "-f", str(compose_file), "build"], app_dir),
        ]

        if any(r.status == "failed" for r in results):
            return results, HealthResult(url="-", status="failed", http_status=None, detail="Build failed before deploy."), None

        up_result = self._run_command("compose-up", [docker, "compose", "-f", str(compose_file), "up", "-d"], app_dir)
        results.append(up_result)
        if up_result.status == "failed":
            rollback = self._run_command("rollback-down", [docker, "compose", "-f", str(compose_file), "down"], app_dir)
            return results, HealthResult(url="-", status="failed", http_status=None, detail="Deploy failed."), rollback

        health = self._health_check()
        rollback = None
        if health.status == "failed":
            rollback = self._run_command("rollback-down", [docker, "compose", "-f", str(compose_file), "down"], app_dir)
        return results, health, rollback

    def _run_command(self, name: str, command: list[str], cwd: Path) -> CommandResult:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
                check=False,
            )
            return CommandResult(
                name=name,
                command=" ".join(command),
                status="passed" if completed.returncode == 0 else "failed",
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                name=name,
                command=" ".join(command),
                status="failed",
                exit_code=None,
                stdout=exc.stdout or "",
                stderr=f"Timed out after {COMMAND_TIMEOUT} seconds. {exc.stderr or ''}",
            )
        except OSError as exc:
            return CommandResult(
                name=name,
                command=" ".join(command),
                status="failed",
                exit_code=None,
                stdout="",
                stderr=str(exc),
            )

    def _health_check(self) -> HealthResult:
        urls = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/v1/health",
            "http://localhost:3000/health",
            "http://localhost/health",
        ]
        last_detail = ""
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=HEALTH_TIMEOUT) as response:
                    status = getattr(response, "status", None)
                    if status and 200 <= status < 400:
                        return HealthResult(url=url, status="passed", http_status=status, detail="Health endpoint responded successfully.")
                    last_detail = f"HTTP {status}"
            except urllib.error.HTTPError as exc:
                last_detail = f"HTTP {exc.code}: {exc.reason}"
            except Exception as exc:
                last_detail = str(exc)
        return HealthResult(url=urls[-1], status="failed", http_status=None, detail=last_detail or "No health endpoint responded.")

    def _generate_file(
        self,
        path: str,
        lang: str,
        ctx_type: str,
        docs: dict[str, str],
        model: str | None,
        tech_stack: dict | None = None,
    ) -> str | None:
        context = self._build_context(ctx_type, docs)
        purposes = _purposes_for_stack(tech_stack)
        purpose = purposes.get(ctx_type, f"Generate {path}")
        prompt = _FILE_TEMPLATE.format(path=path, lang=lang, purpose=purpose, context=context)
        for attempt in range(2):
            try:
                raw = _llm.call_ollama(
                    system_prompt=_SYSTEM_PROMPT.format(
                        tech_stack_info=_tech_stack_description(tech_stack),
                    ),
                    user_prompt=prompt,
                    model=model,
                    timeout=FILE_TIMEOUT,
                    response_format=None,
                )
                content = _llm.strip_code_fences(raw)
                if len(content) >= MIN_FILE_CHARS:
                    return content
                logger.warning("DevOps file %s: short output attempt %d", path, attempt + 1)
            except Exception as exc:
                logger.warning("DevOps file %s error attempt %d: %s", path, attempt + 1, exc)
        return None

    def _build_context(self, ctx_type: str, docs: dict[str, str]) -> str:
        arch = _trunc(docs["architecture"], 3000)
        db = _trunc(docs["database"], 2000)
        api = _trunc(docs["api_spec"], 2000)
        fsd = _trunc(docs["fsd"], 1500)
        pname = docs["project_name"]

        if ctx_type in ("backend_docker", "frontend_docker", "github_ci"):
            return f"PROJECT: {pname}\n\nARCHITECTURE:\n{arch}"
        if ctx_type in ("compose_dev", "compose_prod", "env_example"):
            return f"PROJECT: {pname}\n\nARCHITECTURE:\n{arch}\n\nDATABASE DESIGN:\n{db}"
        if ctx_type == "nginx":
            return f"PROJECT: {pname}\n\nAPI SPEC:\n{api}"
        if ctx_type == "readme":
            return f"PROJECT: {pname}\n\nFSD:\n{fsd}\n\nARCHITECTURE:\n{arch}"
        return arch

    def _write_file(self, app_dir: Path, rel_path: str, content: str) -> None:
        safe_rel = re.sub(r"\.\.+[/\\]", "", rel_path).lstrip("/\\")
        full_path = app_dir / safe_rel
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def _get_output_dir(self, project_id: uuid.UUID) -> Path:
        project = self.session.get(Project, project_id)
        workspace = _container_workspace_path(project.workspace_path if project else None)
        safe_name = _safe_name(project.name if project else "project")
        return Path(workspace) / safe_name / "generated_app"

    def _get_run(self, run_id: uuid.UUID) -> PipelineRun:
        run = self.session.get(PipelineRun, run_id)
        if not run:
            raise ValueError(f"PipelineRun {run_id} not found")
        return run

    def _get_step(self, run_id: uuid.UUID) -> PipelineStep:
        step = self.session.exec(
            select(PipelineStep).where(
                PipelineStep.pipeline_run_id == run_id,
                PipelineStep.step_name == STEP_NAME,
            )
        ).first()
        if not step:
            raise ValueError(f"PipelineStep {STEP_NAME} not found for run {run_id}")
        return step

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(select(Agent).where(Agent.name == AGENT_NAME)).first()

    def _load_source_documents(self, project_id: uuid.UUID) -> tuple[Document, Document, Document, Document]:
        def _latest(doc_type: DocumentType) -> Optional[Document]:
            return self.session.exec(
                select(Document)
                .where(Document.project_id == project_id, Document.document_type == doc_type)
                .order_by(Document.created_at.desc())  # type: ignore[union-attr]
            ).first()

        arch = _latest(DocumentType.architecture_design)
        db = _latest(DocumentType.database_design)
        api = _latest(DocumentType.api_spec)
        fsd = _latest(DocumentType.fsd)
        missing = [name for name, doc in [("Architecture", arch), ("Database", db), ("API Spec", api), ("FSD", fsd)] if not doc]
        if missing:
            raise ValueError(f"Missing source documents: {', '.join(missing)}")
        return arch, db, api, fsd  # type: ignore[return-value]

    def _log_activity(self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str) -> None:
        self.session.add(ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        ))
