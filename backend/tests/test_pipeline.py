"""Tests for the 6-agent pipeline: Requirement → Gap Analysis → BA → SA → UX → Developer Agent."""
import json
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient


# ── helpers ────────────────────────────────────────────────────────────────────

def _create_project(client: TestClient) -> dict:
    r = client.post("/api/v1/projects", json={"name": "Sprint-12 project", "created_by": "tester"})
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


def _approve_through_gate(client: TestClient, project_id: str, run_id: str, *gate_step_names: str) -> None:
    """Approve multiple gates in order."""
    for step_name in gate_step_names:
        step = _get_step(client, project_id, run_id, step_name)
        _approve(client, project_id, run_id, step["id"])


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
            "question": "How should users authenticate?",
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

_MOCK_SA_OUTPUT = json.dumps({
    "architecture": {
        "system_type": "Web Application",
        "components": [
            {
                "id": "COMP-001",
                "name": "Web Frontend",
                "type": "frontend",
                "technology": "React + Vite + TypeScript",
                "description": "SPA for user expense submission and manager approval",
                "responsibilities": ["Display expense forms", "Show approval dashboard"],
                "requirement_refs": ["FR-001", "FR-002"],
            },
            {
                "id": "COMP-002",
                "name": "API Server",
                "type": "backend",
                "technology": "FastAPI",
                "description": "REST API for expense management logic and business rules",
                "responsibilities": ["Handle expense CRUD", "Enforce business rules", "Send notifications"],
                "requirement_refs": ["FR-001", "FR-002", "FR-003"],
            },
            {
                "id": "COMP-003",
                "name": "PostgreSQL Database",
                "type": "database",
                "technology": "PostgreSQL 15",
                "description": "Primary data store for users, expenses, and audit logs",
                "responsibilities": ["Store expense records", "Maintain audit trail"],
                "requirement_refs": ["NFR-001"],
            },
        ],
        "deployment_notes": "Single-server deployment for MVP.",
        "security_considerations": [
            "JWT authentication required for all endpoints",
            "Role-based access: employee vs manager",
        ],
        "integration_points": [
            {"system": "Email Server", "protocol": "SMTP", "description": "Send notifications per FR-003"},
        ],
    },
    "database": {
        "tables": [
            {
                "id": "DB-001",
                "name": "users",
                "description": "System users",
                "columns": [
                    {"name": "id", "type": "UUID", "nullable": False, "description": "Primary key"},
                    {"name": "email", "type": "VARCHAR(255)", "nullable": False, "description": "User email"},
                    {"name": "role", "type": "VARCHAR(50)", "nullable": False, "description": "employee or manager"},
                ],
                "requirement_ref": "FR-001",
            },
            {
                "id": "DB-002",
                "name": "expense_requests",
                "description": "Expense requests",
                "columns": [
                    {"name": "id", "type": "UUID", "nullable": False, "description": "Primary key"},
                    {"name": "user_id", "type": "UUID", "nullable": False, "description": "FK → users.id"},
                    {"name": "amount", "type": "DECIMAL(12,2)", "nullable": False, "description": "Amount"},
                    {"name": "status", "type": "VARCHAR(50)", "nullable": False, "description": "Status"},
                ],
                "requirement_ref": "FR-001",
            },
        ],
        "relationships": [
            {"from_table": "expense_requests", "to_table": "users", "type": "many_to_one", "description": "Each expense belongs to one user"},
        ],
    },
    "api_spec": {
        "base_url": "/api/v1",
        "endpoints": [
            {
                "id": "API-001",
                "method": "POST",
                "path": "/expenses",
                "description": "Submit a new expense request",
                "request_fields": [
                    {"name": "amount", "type": "number", "required": True, "description": "Expense amount"},
                    {"name": "description", "type": "string", "required": True, "description": "Purpose"},
                ],
                "response_fields": [
                    {"name": "id", "type": "string", "required": True, "description": "Created expense ID"},
                    {"name": "status", "type": "string", "required": True, "description": "pending"},
                ],
                "requirement_ref": "FR-001",
            },
            {
                "id": "API-002",
                "method": "POST",
                "path": "/expenses/{id}/approve",
                "description": "Manager approves an expense",
                "request_fields": [],
                "response_fields": [
                    {"name": "status", "type": "string", "required": True, "description": "approved"},
                ],
                "requirement_ref": "FR-002",
            },
        ],
    },
})

_MOCK_UX_OUTPUT = json.dumps({
    "screens": [
        {
            "id": "UI-001",
            "name": "Expense Submission",
            "description": "Employee fills in and submits a new expense request",
            "user_role": "employee",
            "requirement_refs": ["FR-001"],
            "fields": [
                {"name": "amount", "type": "number", "required": True, "validation": "Must be greater than 0", "description": "Expense amount in THB"},
                {"name": "description", "type": "textarea", "required": True, "validation": "Max 500 characters", "description": "Purpose of the expense"},
                {"name": "receipt", "type": "file", "required": False, "validation": "PDF or image, max 5MB", "description": "Receipt attachment"},
            ],
            "actions": ["Submit", "Cancel"],
            "navigation": ["My Expenses List"],
        },
        {
            "id": "UI-002",
            "name": "Manager Approval Dashboard",
            "description": "Manager views and acts on pending expense requests from their team",
            "user_role": "manager",
            "requirement_refs": ["FR-002"],
            "fields": [],
            "actions": ["Approve", "Reject"],
            "navigation": ["Expense Detail", "My Team Overview"],
        },
    ],
    "user_flows": [
        {
            "id": "FLOW-001",
            "name": "Submit Expense Flow",
            "steps": [
                "1. Employee navigates to Expense Submission screen",
                "2. Employee fills in amount, description, and optional receipt",
                "3. Employee clicks Submit",
                "4. System validates the form fields",
                "5. System saves the expense with status PENDING",
                "6. System navigates employee to My Expenses List",
            ],
            "requirement_ref": "FR-001",
        },
        {
            "id": "FLOW-002",
            "name": "Manager Approval Flow",
            "steps": [
                "1. Manager opens Manager Approval Dashboard",
                "2. Manager reviews pending expense requests",
                "3. Manager clicks Approve or Reject on a request",
                "4. System updates the expense status",
                "5. System sends email notification to the employee",
            ],
            "requirement_ref": "FR-002",
        },
    ],
})

_MOCK_DEV_OUTPUT = json.dumps({
    "backend_tasks": [
        {
            "id": "TASK-001",
            "category": "backend",
            "title": "Implement POST /expenses endpoint",
            "description": "Create FastAPI route that accepts expense submission payload, validates business rules, and persists to expense_requests table.",
            "requirement_refs": ["FR-001"],
            "api_refs": ["API-001"],
            "db_refs": ["DB-002"],
            "screen_refs": ["UI-001"],
            "priority": "High",
            "estimated_hours": 4,
        },
        {
            "id": "TASK-002",
            "category": "backend",
            "title": "Implement POST /expenses/{id}/approve endpoint",
            "description": "Create FastAPI route for manager approval action, update expense status to APPROVED, and trigger email notification service.",
            "requirement_refs": ["FR-002"],
            "api_refs": ["API-002"],
            "db_refs": ["DB-002"],
            "screen_refs": ["UI-002"],
            "priority": "High",
            "estimated_hours": 4,
        },
    ],
    "frontend_tasks": [
        {
            "id": "TASK-003",
            "category": "frontend",
            "title": "Build Expense Submission screen",
            "description": "React component for expense submission form with amount, description, and receipt file upload fields per UI-001 spec.",
            "requirement_refs": ["FR-001"],
            "api_refs": ["API-001"],
            "db_refs": [],
            "screen_refs": ["UI-001"],
            "priority": "High",
            "estimated_hours": 6,
        },
        {
            "id": "TASK-004",
            "category": "frontend",
            "title": "Build Manager Approval Dashboard",
            "description": "React component showing pending expense list with Approve/Reject buttons per UI-002 spec.",
            "requirement_refs": ["FR-002"],
            "api_refs": ["API-002"],
            "db_refs": [],
            "screen_refs": ["UI-002"],
            "priority": "High",
            "estimated_hours": 6,
        },
    ],
    "database_migrations": [
        {
            "id": "MIG-001",
            "table": "users",
            "operation": "create_table",
            "description": "Create users table with id, email, role columns per DB-001 spec.",
            "db_ref": "DB-001",
        },
        {
            "id": "MIG-002",
            "table": "expense_requests",
            "operation": "create_table",
            "description": "Create expense_requests table with FK to users per DB-002 spec.",
            "db_ref": "DB-002",
        },
    ],
    "total_estimated_hours": 20,
    "notes": [
        "JWT authentication middleware must be set up before TASK-001 and TASK-002.",
        "Email notification service integration is a dependency for TASK-002.",
    ],
})

# LLM call sequences
_BOTH_LLM_OUTPUTS  = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT]                                                                # Gate 1
_ALL_LLM_OUTPUTS   = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT, _MOCK_BA_OUTPUT]                                               # Gate 2
_FULL_LLM_OUTPUTS  = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT, _MOCK_BA_OUTPUT, _MOCK_SA_OUTPUT]                              # Gate 3
_MAX_LLM_OUTPUTS   = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT, _MOCK_BA_OUTPUT, _MOCK_SA_OUTPUT, _MOCK_UX_OUTPUT]             # Gate 4
_ULTRA_LLM_OUTPUTS = [_MOCK_REQ_OUTPUT, _MOCK_GAP_OUTPUT, _MOCK_BA_OUTPUT, _MOCK_SA_OUTPUT, _MOCK_UX_OUTPUT, _MOCK_DEV_OUTPUT]  # Gate 5


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
    assert {"requirement_summary", "gap_analysis_report"} == doc_types


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
    assert {s["step_name"] for s in steps} == {"requirement_summary", "gap_analysis"}
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

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "waiting_for_user"
    assert final_run["current_step"] == "ba_documents"


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_ba_agent_creates_three_documents(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 5
    doc_types = {d["document_type"] for d in docs["items"]}
    assert {"requirement_summary", "gap_analysis_report", "brd", "fsd", "user_story"} == doc_types


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_brd_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis")

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
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "fsd")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "FSD-001" in doc["content_markdown"]
    assert "FSD-002" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_ALL_LLM_OUTPUTS)
def test_user_story_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "user_story")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "US-001" in doc["content_markdown"]
    assert "US-002" in doc["content_markdown"]


# ── Gate 2 → SA Agent (step 4) ─────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_FULL_LLM_OUTPUTS)
def test_approve_gate2_triggers_sa_agent(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    _approve_through_gate(client, project["id"], run_id, "gap_analysis")
    ba_step = _get_step(client, project["id"], run_id, "ba_documents")
    result = _approve(client, project["id"], run_id, ba_step["id"])
    assert result["next"] == "sa_documents"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "waiting_for_user"
    assert final_run["current_step"] == "sa_documents"


@patch("app.llm.client.call_ollama", side_effect=_FULL_LLM_OUTPUTS)
def test_sa_agent_creates_three_documents(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis", "ba_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 8
    doc_types = {d["document_type"] for d in docs["items"]}
    assert {"requirement_summary", "gap_analysis_report", "brd", "fsd", "user_story",
            "architecture_design", "database_design", "api_spec"} == doc_types


@patch("app.llm.client.call_ollama", side_effect=_FULL_LLM_OUTPUTS)
def test_architecture_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis", "ba_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "architecture_design")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "COMP-001" in doc["content_markdown"]
    assert "COMP-002" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_FULL_LLM_OUTPUTS)
def test_database_design_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis", "ba_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "database_design")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "DB-001" in doc["content_markdown"]
    assert "DB-002" in doc["content_markdown"]


@patch("app.llm.client.call_ollama", side_effect=_FULL_LLM_OUTPUTS)
def test_api_spec_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"], "gap_analysis", "ba_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "api_spec")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "API-001" in doc["content_markdown"]
    assert "API-002" in doc["content_markdown"]


# ── Gate 3 → UX Agent (step 5) ─────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_MAX_LLM_OUTPUTS)
def test_approve_gate3_triggers_ux_agent(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    _approve_through_gate(client, project["id"], run_id, "gap_analysis", "ba_documents")
    sa_step = _get_step(client, project["id"], run_id, "sa_documents")
    result = _approve(client, project["id"], run_id, sa_step["id"])
    assert result["next"] == "ux_documents"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "waiting_for_user"
    assert final_run["current_step"] == "ux_documents"


@patch("app.llm.client.call_ollama", side_effect=_MAX_LLM_OUTPUTS)
def test_ux_agent_creates_screen_spec(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 9
    doc_types = {d["document_type"] for d in docs["items"]}
    assert "screen_spec" in doc_types


@patch("app.llm.client.call_ollama", side_effect=_MAX_LLM_OUTPUTS)
def test_screen_spec_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "screen_spec")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "UI-001" in doc["content_markdown"]
    assert "UI-002" in doc["content_markdown"]
    assert "FLOW-001" in doc["content_markdown"]
    assert "FLOW-002" in doc["content_markdown"]
    assert "FR-001" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_MAX_LLM_OUTPUTS)
def test_list_steps_after_ux(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents")

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}/steps").json()
    assert len(steps) == 5
    for s in steps:
        assert s["status"] == "completed"


# ── Gate 4 → Developer Agent (step 6) ──────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_approve_gate4_triggers_dev_agent(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    _approve_through_gate(client, project["id"], run_id,
                          "gap_analysis", "ba_documents", "sa_documents")
    ux_step = _get_step(client, project["id"], run_id, "ux_documents")
    result = _approve(client, project["id"], run_id, ux_step["id"])
    assert result["next"] == "dev_tasks"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "waiting_for_user"
    assert final_run["current_step"] == "dev_tasks"


@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_dev_agent_creates_task_list(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents", "ux_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    assert docs["total"] == 10
    doc_types = {d["document_type"] for d in docs["items"]}
    assert "code_task_list" in doc_types


@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_task_list_content(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents", "ux_documents")

    docs = client.get(f"/api/v1/projects/{project['id']}/documents").json()
    doc_id = next(d["id"] for d in docs["items"] if d["document_type"] == "code_task_list")
    doc = client.get(f"/api/v1/projects/{project['id']}/documents/{doc_id}").json()
    assert "TASK-001" in doc["content_markdown"]
    assert "TASK-002" in doc["content_markdown"]
    assert "TASK-003" in doc["content_markdown"]
    assert "TASK-004" in doc["content_markdown"]
    assert "MIG-001" in doc["content_markdown"]
    assert "MIG-002" in doc["content_markdown"]
    assert "FR-001" in doc["content_markdown"]
    assert "API-001" in doc["content_markdown"]
    assert doc["status"] == "review"


@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_list_steps_after_dev(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    _approve_through_gate(client, project["id"], run["id"],
                          "gap_analysis", "ba_documents", "sa_documents", "ux_documents")

    steps = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run['id']}/steps").json()
    assert len(steps) == 6
    for s in steps:
        assert s["status"] == "completed"


# ── Gate 5 ─────────────────────────────────────────────────────────────────────

@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_approve_gate5_completes_run(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    _approve_through_gate(client, project["id"], run_id,
                          "gap_analysis", "ba_documents", "sa_documents", "ux_documents")
    dev_step = _get_step(client, project["id"], run_id, "dev_tasks")
    result = _approve(client, project["id"], run_id, dev_step["id"])
    assert result["status"] == "approved"

    final_run = client.get(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}").json()
    assert final_run["status"] == "completed"


@patch("app.llm.client.call_ollama", side_effect=_ULTRA_LLM_OUTPUTS)
def test_approve_wrong_state_returns_400(mock_llm, client: TestClient):
    project = _create_project(client)
    _create_input(client, project["id"])
    run = _run_pipeline(client, project["id"])
    run_id = run["id"]

    # All five gates → run = completed
    _approve_through_gate(client, project["id"], run_id,
                          "gap_analysis", "ba_documents", "sa_documents",
                          "ux_documents", "dev_tasks")

    dev_step = _get_step(client, project["id"], run_id, "dev_tasks")
    r = client.post(f"/api/v1/projects/{project['id']}/pipeline/runs/{run_id}/steps/{dev_step['id']}/approve")
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_STATE"


@patch("app.llm.client.call_ollama", side_effect=_BOTH_LLM_OUTPUTS)
def test_approve_wrong_step_returns_400(mock_llm, client: TestClient):
    """Approving req_summary step while run is at Gate 1 must fail."""
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
