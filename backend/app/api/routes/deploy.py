"""Deploy API — trigger Docker Compose deployment of the generated app."""
import asyncio
import hashlib
import json
import logging
import re
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db.models import Project
from app.db.session import get_session

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Path helpers ───────────────────────────────────────────────────────────────

def _resolve_app_dir(project: Project) -> Optional[Path]:
    raw = project.workspace_path or "/workspace"
    path = re.sub(r"^[A-Za-z]:[/\\]workspace", "/workspace", raw, flags=re.IGNORECASE)
    if not path.startswith("/workspace"):
        path = "/workspace"
    safe_name = re.sub(r"[^\w\-]", "_", project.name or "project")
    return Path(path) / safe_name / "generated_app"


def _project_slug(project_id: uuid.UUID) -> str:
    return f"sdlc_{str(project_id).replace('-', '')[:12]}"


def _assigned_port(project_id: uuid.UUID) -> int:
    h = int(hashlib.md5(str(project_id).encode()).hexdigest(), 16)
    return 9100 + (h % 800)


def _state_file(app_dir: Path) -> Path:
    return app_dir / ".deploy_state.json"


def _read_state(app_dir: Path) -> dict:
    sf = _state_file(app_dir)
    if sf.is_file():
        try:
            return json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"status": "not_deployed"}


def _write_state(app_dir: Path, state: dict) -> None:
    _state_file(app_dir).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Docker compose helpers ─────────────────────────────────────────────────────

def _clean_yaml(raw: str) -> str:
    """Strip markdown code fences and trailing garbage from YAML text."""
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw).strip()
    m = re.match(r"^```[\w.-]*\n([\s\S]+?)\n```\s*$", raw)
    if m:
        return m.group(1)
    if raw.startswith("```"):
        raw = re.sub(r"^```[\w.-]*\n?", "", raw)
    raw = re.sub(r"\n```[\s\S]*$", "", raw)
    return raw.strip()


def _find_frontend_service(compose_file: Path) -> tuple[str, int]:
    """Return (service_name, container_port) for the web-facing service."""
    try:
        import yaml  # type: ignore[import]
        raw = compose_file.read_text(encoding="utf-8")
        data = yaml.safe_load(_clean_yaml(raw))
        services = data.get("services", {})
        for name, svc in services.items():
            for p in svc.get("ports", []):
                p_str = str(p)
                for cport in (3000, 80, 8080, 443):
                    if f":{cport}" in p_str:
                        return name, cport
        for fallback in ("frontend", "web", "app", "nginx"):
            if fallback in services:
                return fallback, 3000
        first = next(iter(services), None)
        return (first or "frontend"), 3000
    except Exception as exc:
        logger.warning("Could not parse compose file: %s", exc)
        return "frontend", 3000


def _patch_dockerfile_project_names(app_dir: Path) -> None:
    """Fix mismatched project filenames and framework versions in Dockerfiles."""
    dockerfile = app_dir / "Dockerfile"
    if not dockerfile.is_file():
        return

    content = dockerfile.read_text(encoding="utf-8")

    # Detect .NET SDK version used in Dockerfile (e.g. dotnet/sdk:6.0 → net6.0)
    sdk_match = re.search(r'dotnet/sdk:([\d.]+)', content)
    dockerfile_tfm = f"net{sdk_match.group(1)}" if sdk_match else None  # e.g. net6.0

    # Fix .csproj filename mismatches
    csproj_in_docker = re.findall(r'[\w.]+\.csproj', content)
    actual_csproj = list(app_dir.glob("*.csproj"))
    if csproj_in_docker and actual_csproj and actual_csproj[0].name not in csproj_in_docker:
        correct_name = actual_csproj[0].name
        stem = correct_name[:-7]
        patched = content
        for wrong in set(csproj_in_docker):
            patched = patched.replace(wrong, correct_name)
        wrong_dlls = re.findall(r'[\w.]+\.dll', patched)
        for wrong_dll in set(wrong_dlls):
            patched = patched.replace(wrong_dll, f"{stem}.dll")
        if patched != content:
            logger.info("Patching Dockerfile: %s → %s", csproj_in_docker[0], correct_name)
            content = patched
            dockerfile.write_text(content, encoding="utf-8")

    # Fix .csproj target framework to match Dockerfile SDK
    if dockerfile_tfm and actual_csproj:
        csproj_file = actual_csproj[0]
        csproj_content = csproj_file.read_text(encoding="utf-8")
        # Replace old/incompatible frameworks (net4xx, net472, etc.) with dockerfile TFM
        new_csproj = re.sub(
            r'<TargetFramework>net[\d.]+(?:472|48|45|46|47)?</TargetFramework>',
            f'<TargetFramework>{dockerfile_tfm}</TargetFramework>',
            csproj_content,
        )
        # Fix placeholder assembly names
        new_csproj = re.sub(r'<AssemblyName>YourProjectName</AssemblyName>', f'<AssemblyName>{csproj_file.stem}</AssemblyName>', new_csproj)
        new_csproj = re.sub(r'<RootNamespace>YourProjectName</RootNamespace>', f'<RootNamespace>{csproj_file.stem}</RootNamespace>', new_csproj)
        # Remove WebForms-specific items that break .NET 6+ builds
        new_csproj = re.sub(r'\s*<Content Include="App_Data[^"]*"[^/]*/>\s*', '\n    ', new_csproj)
        new_csproj = re.sub(r'\s*<Content Include="Scripts[^"]*"[^/]*/>\s*', '\n    ', new_csproj)
        new_csproj = re.sub(r'\s*<Content Include="Styles[^"]*"[^/]*/>\s*', '\n    ', new_csproj)
        new_csproj = re.sub(r'\s*<Content Update="Web\.config"[^>]*>.*?</Content>\s*', '\n    ', new_csproj, flags=re.DOTALL)
        # Remove AspNet.Identity (not compatible with .NET 6+)
        new_csproj = re.sub(r'\s*<PackageReference Include="Microsoft\.AspNet\.[^"]*"[^/]*/>\s*', '\n    ', new_csproj)
        if new_csproj != csproj_content:
            logger.info("Patching %s: target framework and assembly names", csproj_file.name)
            csproj_file.write_text(new_csproj, encoding="utf-8")


def _patch_build_contexts(app_dir: Path, compose_file: Path) -> bool:
    """Rewrite any build.context paths that don't exist → '.'. Returns True if patched."""
    content = compose_file.read_text(encoding="utf-8")
    changed = False

    def _replace(m: re.Match) -> str:
        nonlocal changed
        prefix = m.group(1)          # "context: "
        ctx = m.group(2).strip().strip("'\"")  # the context value
        if ctx in (".", "./"):
            return m.group(0)
        ctx_path = (app_dir / ctx).resolve()
        if not ctx_path.is_dir():
            changed = True
            logger.info("Patching build context '%s' -> '.' in %s", ctx, compose_file.name)
            return prefix + "."
        return m.group(0)

    patched = re.sub(r"(context:\s*)([^\n]+)", _replace, content)
    if changed:
        compose_file.write_text(patched, encoding="utf-8")
    return changed


def _write_override(app_dir: Path, service: str, host_port: int, container_port: int) -> None:
    content = (
        f"services:\n"
        f"  {service}:\n"
        f"    ports:\n"
        f'      - "{host_port}:{container_port}"\n'
    )
    (app_dir / "docker-compose.override.yml").write_text(content, encoding="utf-8")


def _run_compose(app_dir: Path, slug: str, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    cmd = ["docker", "compose", "-p", slug, *args]
    return subprocess.run(cmd, cwd=str(app_dir), capture_output=True, text=True, timeout=timeout)


def _docker_available() -> bool:
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Background deploy task ─────────────────────────────────────────────────────

def _do_deploy(app_dir: Path, slug: str, state: dict) -> None:
    """Run docker compose up -d --build in a background thread."""
    try:
        result = _run_compose(app_dir, slug, "up", "-d", "--build", timeout=300)
        if result.returncode != 0:
            state["status"] = "failed"
            state["error"] = (result.stderr or result.stdout or "Unknown error")[-3000:]
        else:
            state["status"] = "running"
            state["error"] = None
    except subprocess.TimeoutExpired:
        state["status"] = "failed"
        state["error"] = "Deploy timed out after 5 minutes."
    except FileNotFoundError:
        state["status"] = "failed"
        state["error"] = "Docker CLI not found. Check docker.sock mount and Dockerfile."
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
    _write_state(app_dir, state)


# ── Schemas ────────────────────────────────────────────────────────────────────

class DeployStatus(BaseModel):
    status: str  # not_deployed | deploying | running | stopped | failed
    port: Optional[int] = None
    app_url: Optional[str] = None
    project_name: Optional[str] = None
    last_deployed_at: Optional[str] = None
    error: Optional[str] = None
    has_compose_file: bool = False
    docker_available: bool = False
    services: list[dict] = []


class DeployLogsResponse(BaseModel):
    logs: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/{project_id}/deploy/status", response_model=DeployStatus)
def get_deploy_status(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    app_dir = _resolve_app_dir(project)
    has_compose = bool(app_dir and (app_dir / "docker-compose.yml").is_file())
    docker_ok = _docker_available()

    if not app_dir or not app_dir.is_dir():
        return DeployStatus(status="not_deployed", has_compose_file=False, docker_available=docker_ok)

    state = _read_state(app_dir)

    # Live-verify running status
    if state.get("status") == "running":
        slug = state.get("project_name") or _project_slug(project_id)
        try:
            r = _run_compose(app_dir, slug, "ps", "--format", "json", timeout=10)
            services: list[dict] = []
            for line in (r.stdout or "").strip().splitlines():
                try:
                    services.append(json.loads(line))
                except Exception:
                    pass
            if not services:
                state["status"] = "stopped"
                _write_state(app_dir, state)
            state["services"] = services
        except Exception:
            pass

    return DeployStatus(
        status=state.get("status", "not_deployed"),
        port=state.get("port"),
        app_url=state.get("app_url"),
        project_name=state.get("project_name"),
        last_deployed_at=state.get("last_deployed_at"),
        error=state.get("error"),
        has_compose_file=has_compose,
        docker_available=docker_ok,
        services=state.get("services", []),
    )


@router.post("/{project_id}/deploy/start", response_model=DeployStatus)
def start_deploy(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    app_dir = _resolve_app_dir(project)
    if not app_dir or not app_dir.is_dir():
        raise HTTPException(status_code=422, detail="No generated app found. Run the DevOps agent first.")

    compose_file = app_dir / "docker-compose.yml"
    if not compose_file.is_file():
        raise HTTPException(status_code=422, detail="docker-compose.yml not found. DevOps agent must run first.")

    slug = _project_slug(project_id)
    port = _assigned_port(project_id)

    # Fix invalid build contexts (e.g. ./backend that doesn't exist)
    _patch_build_contexts(app_dir, compose_file)
    # Fix mismatched project filenames in Dockerfiles
    _patch_dockerfile_project_names(app_dir)

    service, cport = _find_frontend_service(compose_file)
    _write_override(app_dir, service, port, cport)

    state: dict = {
        "status": "deploying",
        "port": port,
        "project_name": slug,
        "app_url": f"http://localhost:{port}",
        "last_deployed_at": datetime.now(UTC).isoformat(),
        "error": None,
        "services": [],
    }
    _write_state(app_dir, state)

    background_tasks.add_task(_do_deploy, app_dir, slug, state)

    return DeployStatus(
        status="deploying",
        port=port,
        app_url=f"http://localhost:{port}",
        project_name=slug,
        last_deployed_at=state["last_deployed_at"],
        has_compose_file=True,
        docker_available=True,
    )


@router.post("/{project_id}/deploy/stop", response_model=DeployStatus)
def stop_deploy(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    app_dir = _resolve_app_dir(project)
    if not app_dir or not app_dir.is_dir():
        raise HTTPException(status_code=422, detail="No generated app found")

    state = _read_state(app_dir)
    slug = state.get("project_name") or _project_slug(project_id)
    has_compose = (app_dir / "docker-compose.yml").is_file()

    try:
        _run_compose(app_dir, slug, "down", timeout=60)
        state["status"] = "stopped"
        state["error"] = None
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)

    _write_state(app_dir, state)
    return DeployStatus(
        status=state["status"],
        port=state.get("port"),
        app_url=state.get("app_url"),
        project_name=slug,
        error=state.get("error"),
        has_compose_file=has_compose,
        docker_available=_docker_available(),
    )


@router.get("/{project_id}/deploy/logs", response_model=DeployLogsResponse)
def get_deploy_logs(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    app_dir = _resolve_app_dir(project)
    if not app_dir or not app_dir.is_dir():
        raise HTTPException(status_code=422, detail="No generated app found")

    state = _read_state(app_dir)
    slug = state.get("project_name") or _project_slug(project_id)

    try:
        r = _run_compose(app_dir, slug, "logs", "--tail=300", "--no-color", timeout=30)
        logs = r.stdout or ""
        if r.returncode != 0 and r.stderr:
            logs = (logs + "\n\nSTDERR:\n" + r.stderr).strip()
        if not logs:
            logs = "(No logs available. Containers may not be running.)"
    except FileNotFoundError:
        logs = "Docker not available in this container. Check docker.sock mount."
    except Exception as exc:
        logs = f"Error fetching logs: {exc}"

    return DeployLogsResponse(logs=logs)
