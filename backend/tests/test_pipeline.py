"""Tests for the full 2-agent pipeline: Requirement Agent → Gap Analysis Agent."""
import json
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient


# ── helpers ────────────────────────────────────────────────────────────────────

def _create_project(client: TestClient) -> dict:
    r = client.post("/api/v1/projects", json={"name": "Sprint-9 project", "created_by": "tester"})
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


def _run_pipeline(client: TestClient, project_id: str) -> dict:
    r = client.post(f"/api/v1/projects/{project_id}/pipeline/runs")
    assert r.status_code == 201
    return r.json()


_MOCK_REQ_OUTPUT = json.dumps({
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
    "assumptions": ["Users have email access"],
    "constraints": ["Must integrate with existing email server"],
    "business_rules": [{"id": "BR-001", "rule": "Expenses above 50,000 THB require CFO approval"}],
    "open_questions": ["What is the maximum expense amount?"],
})

_MOCK_GAP_OUTPUT = json.dumps({
    "overall_assessment": "Requirements are mostly complete but missing security and notification detail.",
    "completeness_score": 70,
    "gaps": [
        {
            "id": "GAP-001",
            "category": "missing_security_requirement",
            "severity": "High",
            "description": "No authentication or authorization requirement stated.",
            "related_requirement_id": None,
            "question": "How should users authenticate? Is role-based access control required?",
        },
        {
            "id": "GAP-002",
            "category": "missing_non_functional_requirement",
            "severity": "Medium",
            "description": "No data retention or audit log requirement.",
            "related_requirement_id": "FR-001",
            "question": "How long should expense records be retained?",
        },
    ],
    "recommendations": [
        "Add authentication and authorization requirements.",
        "Define data retention policy.",
    ],
})

# Both agents return valid mock output
_BOTH_LLM_OUTPUTS = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT]


# ── guard tests (no LLM) ───────────────────────────────────────────────────────

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


# ── full pipeline (2 agents) ───────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_full_pipeline_creates_two_documents(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}").json()
    assert final_run["status"] == "waiting_for_user"

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 2
    doc_types = {d["document_type"] for d in docs["items"]}
    assert "requirement_summary" in doc_types
    assert "gap_analysis_report" in doc_types


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_requirement_summary_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    req_doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "requirement_summary")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{req_doc_id}").json()
    assert "FR-001" in doc["content_markdown"]
    assert "NFR-001" in doc["content_markdown"]
    assert "BR-001" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_gap_analysis_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    gap_doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "gap_analysis_report")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{gap_doc_id}").json()
    assert "GAP-001" in doc["content_markdown"]
    assert "GAP-002" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_list_steps_two_completed(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}/steps").json()
    assert len(steps) == 2
    step_names = {s["step_name"] for s in steps}
    assert step_names == {"requirement_summary", "gap_analysis"}
    for s in steps:
        assert s["status"] == "completed"


# ── Gate 1: approve / reject ───────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_approve_gate1(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    # Get the gap_analysis step id
    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps").json()
    gap_step = next(s for s in steps if s["step_name"] == "gap_analysis")

    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{gap_step['id']}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "completed"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_reject_gate1(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps").json()
    gap_step = next(s for s in steps if s["step_name"] == "gap_analysis")

    r = client.post(
        f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{gap_step['id']}/reject",
        json={"reason": "Gap analysis is incomplete, missing performance requirements"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "failed"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_approve_wrong_state_returns_400(mock_llm, client: TestClient):
    """Cannot approve a run that is not waiting_for_user."""
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps").json()
    gap_step = next(s for s in steps if s["step_name"] == "gap_analysis")

    # Approve once (valid)
    client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{gap_step['id']}/approve")

    # Approve again (invalid — run is now completed, not waiting_for_user)
    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{gap_step['id']}/approve")
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_STATE"


# ── failure path ───────────────────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", return_value="INVALID JSON {{")
def test_llm_failure_marks_run_failed(mock_llm, client: TestClient):
    """When RequirementAgent's LLM call returns bad JSON, run is marked failed."""
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    runs = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs").json()
    assert runs[0]["status"] == "failed"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_document_content_approve(mock_llm, client: TestClient):
    """A document can be approved via the document endpoint regardless of pipeline gate."""
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = docs["items"][0]["id"]

    r = client.post(f"/api/v1/projects/{project['id']}/documents/{doc_id}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"
