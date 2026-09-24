import json
import sys
import time
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.codex_agent import CodexAgent, TaskPacket

root = Path(__file__).resolve().parents[1] / "data" / "sandbox" / "codex_test_project"
root.mkdir(parents=True, exist_ok=True)
(root / "calculator.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
(root / "test_calculator.py").write_text("from calculator import add\n\ndef test_add():\n    assert add(2, 3) == 5\n", encoding="utf-8")
packet = TaskPacket("TASK-CODEX-001", "software engineer", "Add multiply(a, b) to calculator.py and create an automated test.", {}, ["calculator.py", "test_calculator.py", "test_multiply.py"], ["Do not modify files outside allowed scope."], ["multiply returns product", "pytest passes"], "summary and changed files", ["run pytest"], str(root), ["calculator.py", "test_calculator.py", "test_multiply.py"])
started = time.perf_counter(); agent = CodexAgent(); health = agent.health_check(); result = agent.execute(packet, {"execution_id": "EXEC-CODEX-SANDBOX"}); duration = round(time.perf_counter() - started, 2)
validation = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, capture_output=True, text=True, timeout=60, shell=False)
validated = validation.returncode == 0
print(json.dumps({"health": health, "status": "DONE" if result.metadata.get("status") == "REVIEW" and validated else "FAILED", "exit_code": result.metadata.get("exit_code"), "duration": duration, "changed_files": result.metadata.get("changed_files", []), "validation_passed": validated, "validation_output": (validation.stdout + validation.stderr)[-2000:], "stderr": result.metadata.get("stderr", "")[-1000:], "output": result.output[-2000:]}, ensure_ascii=False))
if health["status"] != "available": raise SystemExit("Codex unavailable")
if not validated: raise SystemExit(1)
