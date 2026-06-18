"""Tests for pipeline routes and the Requirement Agent runner (mocked LLM)."""
import json
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ── helpers ────────────────────────────────────────────────────────────────────

def _create_project(client: TestClient) -> dict:
    r = client.post("/api/v1/projects", json={"name": "Sprint-8 project", "created_by": "tester"})
    assert r.status_code == 201
    return r.json()


def _create_input(client: TestClient, project_id: str) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/inputs",
        json={
            "input_type": "manual_text",
            "title": "Sample requirement",
            "content": "Build a simple expense management system. Users can submit expense requests. Managers can approve or reject them. The system must send email notifications.",
        },
    )
    assert r.status_code == 201
    return r.json()


_MOCK_LLM_OUTPUT = json.dumps({
    "business_objective": "Enable employees to submit and track expense reimbursement requests digitally.",
    "in_scope": ["Expense submission", "Manager approval", "Email notifications"],
    "out_of_scope": ["Mobile app", "Third-party accounting integration"],
    "functional_requirements": [
        {"id": "FR-001", "requirement": "User can submit expense request with amount and description", "source": "manual_text", "priority": "High"},
        {"id": "FR-002", "requirement": "Manager can approve or reject submitted expense requests", "source": "manual_text", "priority": "High"},
        {"id": "FR-003", "requirement": "System sends email notification on approval or rejection", "source": "manual_text", "priority": "Medium"},
    ],
    "non_functional_requirements": [
        {"id": "NFR-001", "requirement": "System must respond within 2 seconds", "category": "Performance", "priority": "Medium"},
    ],
    "stakeholders": [
        {"role": "Employee", "responsibility": "Submit expense requests", "involvement": "User"},
        {"role": "Manager", "responsibility": "Approve or reject requests", "involvement": "Approver"},
    ],
    "assumptions": ["Users have email access", "Managers are pre-configured in the system"],
    "constraints": ["Must integrate with existing email server"],
    "business_rules": [
        {"id": "BR-001", "rule": "Expenses above 50,000 THB require CFO approval"},
    ],
    "open_questions": [
        "What is the maximum expense amount that can be submitted?",
        "Who configures manager assignments?",
    ],
})


# ── tests ──────────────────────────────────────────────────────────────────────

def test_start_pipeline_no_inputs(client: TestClient):
    project = _create_project(client)
    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs")
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "NO_INPUTS"


def test_start_pipeline_project_not_found(client: TestClient):
    r = client.post(f"/api/v1/projects/{uuid.uuid4()}/pipeline/runs")
    assert r.status_code == 404


def test_list_runs_empty(client: TestClient):
    project = _create_project(client)
    r = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs")
    assert r.status_code == 200
    assert r.json() == []


@patch("app.llm.client.call_ollama", return_value=_MOCK_LLM_OUTPUT)
def test_pipeline_run_creates_document(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])

    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs")
    assert r.status_code == 201
    run = r.json()
    assert run["project_id"] == project["id"]
    assert run["status"] in ("pending", "running", "completed")

    # Background task runs synchronously in TestClient
    runs = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs").json()
    assert len(runs) >= 1

    # After background task completes the run should be completed
    run_id = run["id"]
    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "completed"

    # Document should be created
    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 1
    assert docs["items"][0]["document_type"] == "requirement_summary"
    assert docs["items"][0]["status"] == "review"


@patch("app.llm.client.call_ollama", return_value=_MOCK_LLM_OUTPUT)
def test_document_content_has_fr_table(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    client.post(f"/api/v1/projects/{project['id']}/pipeline/runs")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = docs["items"][0]["id"]

    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "FR-001" in doc["content_markdown"]
    assert "FR-002" in doc["content_markdown"]
    assert "NFR-001" in doc["content_markdown"]
    assert "BR-001" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", return_value=_MOCK_LLM_OUTPUT)
def test_document_approve(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    client.post(f"/api/v1/projects/{project['id']}/pipeline/runs")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = docs["items"][0]["id"]

    r = client.post(f"/api/v1/projects/{project['id']}/documents/{doc_id}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


@patch("app.llm.client.call_ollama", return_value="INVALID JSON {{")
def test_pipeline_run_llm_failure_marks_failed(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    client.post(f"/api/v1/projects/{project['id']}/pipeline/runs")

    runs = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs").json()
    assert runs[0]["status"] == "failed"


def test_list_steps(client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])

    with patch("app.llm.client.call_ollama", return_value=_MOCK_LLM_OUTPUT):
        run_resp = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs").json()

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_resp['id']}/steps").json()
    assert len(steps) == 1
    assert steps[0]["step_name"] == "requirement_summary"
    assert steps[0]["status"] == "completed"
