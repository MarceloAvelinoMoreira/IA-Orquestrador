import json
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.engine import OrchestrationEngine
from app.providers import OllamaProvider
from app.schemas import OrchestrationRequest

started = time.perf_counter()
result = OrchestrationEngine(provider=OllamaProvider(timeout=180)).execute(OrchestrationRequest(request="Crie uma API simples para gerenciar tarefas."), use_ollama=True)
elapsed = time.perf_counter() - started
assert result["analysis"] and result["plan"] and result["tasks"] and result["routing"]
print(json.dumps({"status": result["status"], "elapsed_seconds": round(elapsed, 2), "tasks": len(result["tasks"]), "routing_decisions": len(result["routing"])}, ensure_ascii=False))
