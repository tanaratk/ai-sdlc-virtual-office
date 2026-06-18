"""Tests for the 3-agent pipeline: Requirement → Gap Analysis → BA Agent."""
import json
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient


# ── helpers ────────────────────────────────────────────────────────────────────

def _create_project(client: TestClient) -> dict:
    r = client.post("/api/v1/projects", json={"name": "Sprint-10 project", "created_by": "tester"})
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


def _get_step(client: TestClient, project_id: str, run_id: str, step_name: str) -> dict:
    steps = client.get(f"/api/v1/projects/{project_id}/pipeline/runs/{run_id}/steps").json()
    return next(s for s in steps if s["step_name"] == step_name)


def _approve(client: TestClient, project_id: str, run_id: str, step_id: str) -> dict:
    r = client.post(f"/api/v1/projects/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/approve")
    assert r.status_code == 200
    return r.json()


# ── Mock LLM outputs ───────────────────────────────────────────────────────────

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

_MOCK_BA_OUTPUT = json.dumps({
    "brd": {
        "business_need": "The company needs a digital expense management system to reduce manual paperwork and approval delays.",
        "objectives": ["Reduce expense processing time by 50%", "Improve audit trail for compliance"],
        "success_criteria": ["All expense requests processed within 2 business days"],
        "assumptions": ["Users have internet access"],
        "constraints": ["Must comply with Thai accounting regulations"],
        "risks": [{"id": "RISK-001", "description": "User adoption may be slow without training", "impact": "Medium"}],
    },
    "fsd": {
        "system_overview": "A web-based expense management system with submission and approval workflow.",
        "functional_specs": [
            {
                "id": "FSD-001",
                "requirement_ref": "FR-001",
                "feature": "Expense Submission",
                "description": "Users can submit expense requests with amount, description, and receipt attachment.",
                "acceptance_criteria": ["Given a logged-in employee, when they submit an expense, then the request is saved with status PENDING"],
            },
            {
                "id": "FSD-002",
                "requirement_ref": "FR-002",
                "feature": "Manager Approval",
                "description": "Managers can approve or reject submitted expense requests from their team.",
                "acceptance_criteria": ["Given a pending expense, when a manager approves it, then the status changes to APPROVED"],
            },
        ],
    },
    "user_stories": [
        {
            "id": "US-001",
            "requirement_ref": "FR-001",
            "as_a": "employee",
            "i_want": "to submit an expense request with amount and description",
            "so_that": "I can get reimbursed for my work expenses",
            "acceptance_criteria": ["Given I am logged in, when I submit an expense, then it appears in my pending list"],
            "priority": "Must Have",
        },
        {
            "id": "US-002",
            "requirement_ref": "FR-002",
            "as_a": "manager",
            "i_want": "to approve or reject expense requests from my team",
            "so_that": "I can control expense spending within budget",
            "acceptance_criteria": ["Given a pending request, when I approve it, then the employee is notified by email"],
            "priority": "Must Have",
        },
    ],
})

_BOTH_LLM_OUTPUTS = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT]
_ALL_LLM_OUTPUTS = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT, _MOCK_BA_OUTPUT]


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


# ── steps 1+2 (req + gap) ─────────────────────────────────────────────────────

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
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "requirement_summary")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "FR-001" in doc["content_markdown"]
    assert "NFR-001" in doc["content_markdown"]
    assert "BR-001" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_gap_analysis_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "gap_analysis_report")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "GAP-001" in doc["content_markdown"]
    assert "GAP-002" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_list_steps_after_gap_analysis(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}/steps").json()
    assert len(steps) == 2
    step_names = {s["step_name"] for s in steps}
    assert step_names == {"requirement_summary", "gap_analysis"}
    for s in steps:
        assert s["status"] == "completed"


# ── Gate 1 → BA Agent (step 3) ─────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_approve_gate1_triggers_ba_agent(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    gap_step = _get_step(client, project["id"], run_id, "gap_analysis")
    result = _approve(client, project["id"], run_id, gap_step["id"])
    assert result["next"] == "ba_documents"

    # BA Agent ran synchronously — run is now at Gate 2
    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "waiting_for_user"
    assert final_run["current_step"] == "ba_documents"


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_ba_agent_creates_three_documents(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])

    gap_step = _get_step(client, project["id"], run["id"], "gap_analysis")
    _approve(client, project["id"], run["id"], gap_step["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 5
    doc_types = {d["document_type"] for d in docs["items"]}
    assert {"requirement_summary", "gap_analysis_report", "brd", "fsd", "user_story"} == doc_types


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_brd_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    gap_step = _get_step(client, project["id"], run["id"], "gap_analysis")
    _approve(client, project["id"], run["id"], gap_step["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "brd")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "RISK-001" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_fsd_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    gap_step = _get_step(client, project["id"], run["id"], "gap_analysis")
    _approve(client, project["id"], run["id"], gap_step["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "fsd")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "FSD-001" in doc["content_markdown"]
    assert "FSD-002" in doc["content_markdown"]
    assert "FR-001" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_user_story_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    gap_step = _get_step(client, project["id"], run["id"], "gap_analysis")
    _approve(client, project["id"], run["id"], gap_step["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "user_story")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "US-001" in doc["content_markdown"]
    assert "US-002" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_list_steps_after_ba(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    gap_step = _get_step(client, project["id"], run["id"], "gap_analysis")
    _approve(client, project["id"], run["id"], gap_step["id"])

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}/steps").json()
    assert len(steps) == 3
    for s in steps:
        assert s["status"] == "completed"


# ── Gate 2 ─────────────────────────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_approve_gate2_completes_run(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    # Gate 1
    gap_step = _get_step(client, project["id"], run_id, "gap_analysis")
    _approve(client, project["id"], run_id, gap_step["id"])

    # Gate 2
    ba_step = _get_step(client, project["id"], run_id, "ba_documents")
    result = _approve(client, project["id"], run_id, ba_step["id"])
    assert result["status"] == "approved"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "completed"


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_approve_wrong_state_returns_400(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    # Gate 1 + Gate 2 → run = completed
    gap_step = _get_step(client, project["id"], run_id, "gap_analysis")
    _approve(client, project["id"], run_id, gap_step["id"])
    ba_step = _get_step(client, project["id"], run_id, "ba_documents")
    _approve(client, project["id"], run_id, ba_step["id"])

    # Try to approve again — run is completed, not waiting_for_user
    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{ba_step['id']}/approve")
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_STATE"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_approve_wrong_step_returns_400(mock_llm, client: TestClient):
    """Approving req_summary step while run is at Gate 1 (gap_analysis) must fail."""
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    req_step = _get_step(client, project["id"], run_id, "requirement_summary")
    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{req_step['id']}/approve")
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "WRONG_STEP"


# ── Gate 1 reject ──────────────────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_reject_gate1(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    gap_step = _get_step(client, project["id"], run_id, "gap_analysis")
    r = client.post(
        f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{gap_step['id']}/reject",
        json={"reason": "Gap analysis is incomplete, missing performance requirements"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "failed"


# ── failure path ───────────────────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", return_value="INVALID JSON {{")
def test_llm_failure_marks_run_failed(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    runs = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs").json()
    assert runs[0]["status"] == "failed"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_document_approve_via_document_endpoint(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    _run_pipeline(client, project["id"])

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = docs["items"][0]["id"]

    r = client.post(f"/api/v1/projects/{project['id']}/documents/{doc_id}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"
