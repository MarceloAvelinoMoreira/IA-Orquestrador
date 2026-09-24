from pathlib import Path
from app.codex_agent import CodexAgent, TaskPacket


def packet(tmp_path: Path):
    return TaskPacket("TASK-1", "engineer", "do task", {}, [], [], ["done"], "summary", [], str(tmp_path), ["calculator.py"])


def test_task_packet_is_structured(tmp_path):
    text = packet(tmp_path).to_prompt()
    assert "TASK_PACKET_JSON" in text and str(tmp_path).replace("\\", "\\\\") in text


def test_codex_health_unavailable():
    agent = CodexAgent(executable="definitely-not-installed")
    result = agent.health_check()
    assert result["status"] == "unavailable"


def test_codex_execute_mocked(monkeypatch, tmp_path):
    class Completed:
        returncode = 0; stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"done"}}'; stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: Completed())
    result = CodexAgent().execute(packet(tmp_path), {"execution_id": "EXEC-1"})
    assert result.output == "done"
    assert result.metadata["status"] == "REVIEW"
