import pytest
from server import app

@pytest.fixture

def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}

def test_run_tool_success(client):
    resp = client.post("/run_tool/test_echo", json={"text": "hello"})
    assert resp.status_code == 200
    assert resp.get_json() == {"output": "hello"}

def test_run_tool_invalid_tool(client):
    resp = client.post("/run_tool/nonexistent", json={})
    assert resp.status_code == 404

def test_run_tool_no_json(client):
    resp = client.post("/run_tool/test_echo")
    assert resp.status_code == 400
