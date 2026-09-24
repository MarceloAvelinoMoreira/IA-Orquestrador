import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.api import app
from app.config import settings

root = Path(__file__).resolve().parents[1] / "data" / "sandbox" / "e2e_codex_project"
root.mkdir(parents=True, exist_ok=True)
(root / "calculator.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
(root / "test_calculator.py").write_text("from calculator import add\n\ndef test_add():\n    assert add(2, 3) == 5\n", encoding="utf-8")
settings.workspace = root
started = time.perf_counter()
with TestClient(app) as client:
    response = client.post("/orchestrate", json={"request": "Implemente multiply(a, b) em calculator.py e crie um teste automatizado.", "execution_mode": "external"})
elapsed = round(time.perf_counter() - started, 2)
body = response.json()
print(json.dumps({"http_status": response.status_code, "execution_id": body.get("execution_id"), "status": body.get("status"), "tasks": len(body.get("tasks", [])), "analysis": body.get("analysis"), "routing": body.get("routing"), "results": body.get("results"), "persistence": bool(body.get("execution_id")), "elapsed_seconds": elapsed}, ensure_ascii=False))
if response.status_code != 200 or body.get("status") != "DONE": raise SystemExit(1)
