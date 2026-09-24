from fastapi.testclient import TestClient
from app.agents import AgentRegistry, MockAgent
from app.router import Router
from app.api import app


def test_mock_agent_and_registry():
    registry = AgentRegistry(); agent = MockAgent(); registry.register(agent)
    assert registry.get("mock") is agent
    assert "Objective received" in agent.execute("teste").output


def test_router_returns_registered_agent():
    registry = AgentRegistry(); registry.register(MockAgent())
    decision = Router(registry).route("implemente um endpoint")
    assert decision.agent.name == "mock"


def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_task_endpoints():
    with TestClient(app) as client:
        response = client.post("/tasks", json={"title": "Teste", "dependencies": []})
        assert response.status_code == 201
        assert response.json()["status"] == "PENDING"
        assert client.get("/tasks").status_code == 200
