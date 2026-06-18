from fastapi.testclient import TestClient


def test_health(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_project(client: TestClient):
    response = client.post("/api/v1/projects", json={
        "name": "Test Project",
        "description": "A test project",
        "created_by": "test_user",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "active"
    assert "id" in data


def test_list_projects(client: TestClient):
    client.post("/api/v1/projects", json={"name": "P1", "created_by": "u"})
    client.post("/api/v1/projects", json={"name": "P2", "created_by": "u"})
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


def test_get_project(client: TestClient):
    created = client.post("/api/v1/projects", json={"name": "P3", "created_by": "u"}).json()
    response = client.get(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_project_not_found(client: TestClient):
    response = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_project(client: TestClient):
    created = client.post("/api/v1/projects", json={"name": "P4", "created_by": "u"}).json()
    response = client.patch(f"/api/v1/projects/{created['id']}", json={"name": "P4 Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "P4 Updated"


def test_delete_project(client: TestClient):
    created = client.post("/api/v1/projects", json={"name": "P5", "created_by": "u"}).json()
    response = client.delete(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/projects/{created['id']}").status_code == 404


def test_create_requirement_input(client: TestClient):
    project = client.post("/api/v1/projects", json={"name": "P6", "created_by": "u"}).json()
    response = client.post(f"/api/v1/projects/{project['id']}/inputs", json={
        "input_type": "meeting_transcript",
        "title": "Kickoff meeting",
        "content": "We need a checkout redesign.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["input_type"] == "meeting_transcript"
    assert data["project_id"] == project["id"]
