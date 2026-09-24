import json
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.claude_agent import ClaudeAgent
from app.codex_agent import TaskPacket

root = Path(__file__).resolve().parents[1] / "data" / "sandbox" / "claude_test_project"
root.mkdir(parents=True, exist_ok=True)
(root / "calculator.py").write_text("def divide(a, b):\n    return a * b\n", encoding="utf-8")
(root / "test_calculator.py").write_text("from calculator import divide\n\ndef test_divide():\n    assert divide(8, 2) == 4\n", encoding="utf-8")
agent = ClaudeAgent(); health = agent.health_check()
packet = TaskPacket("TASK-CLAUDE-001", "debugging engineer", "Investigate why tests for divide fail, identify root cause, make the minimal correction, and do not modify files outside the workspace.", {}, ["calculator.py", "test_calculator.py"], ["No files outside workspace."], ["divide returns correct quotient"], "root cause and changed files", ["pytest externally"], str(root), ["calculator.py", "test_calculator.py"])
started = time.perf_counter(); result = agent.execute(packet, {"execution_id":"EXEC-CLAUDE-SANDBOX"}); duration = round(time.perf_counter()-started, 2)
validation = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, capture_output=True, text=True, timeout=60, shell=False)
print(json.dumps({"health": health, "status": "DONE" if result.metadata.get("status") == "REVIEW" and validation.returncode == 0 else "FAILED", "selected_executable": str(agent.executable), "duration": duration, "changed_files": result.metadata.get("changed_files", []), "validation": (validation.stdout + validation.stderr)[-2000:], "stderr": result.metadata.get("stderr", "")[-1000:], "output": result.output[-1500:]}, ensure_ascii=False))
if health["status"] != "available" or validation.returncode != 0: raise SystemExit(1)
