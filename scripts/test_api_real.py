import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.api import app

with TestClient(app) as client:
    response = client.post("/orchestrate", json={"request": "Crie uma API simples para gerenciar tarefas."})
    body = response.json()
    print(json.dumps({"http_status": response.status_code, "status": body.get("status"), "execution_id": body.get("execution_id"), "tasks": len(body.get("tasks", [])), "routing": len(body.get("routing", [])), "results": len(body.get("results", []))}, ensure_ascii=False))
    if response.status_code != 200: raise SystemExit(1)
