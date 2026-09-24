from app.capabilities import normalize_capability, normalize_capabilities
from app.agents import AgentRegistry, MockAgent
from app.claude_agent import ClaudeAgent
from app.codex_agent import CodexAgent
from app.router import Router


def test_capability_aliases_and_unknown():
    assert normalize_capability("unit_tests") == "TESTING"
    assert normalize_capability("implementation") == "CODING"
    assert normalize_capability("something_new") == "UNKNOWN"


def test_router_scores_codex_and_claude():
    registry = AgentRegistry(); codex = CodexAgent(); codex.status = "AVAILABLE"; claude = ClaudeAgent(); claude.status = "AVAILABLE"; registry.register(codex); registry.register(claude)
    router = Router(registry)
    assert router.route_task("t1", ["coding"]).score > 0
    assert router.route_task("t2", ["debugging"]).score > 0


def test_claude_unavailable():
    assert ClaudeAgent(executable="not-a-real-claude").health_check()["status"] == "unavailable"
