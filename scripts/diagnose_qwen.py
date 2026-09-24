import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from app.config import settings
from app.inspector import ProjectInspector
from app.prompts.analysis import analysis_prompt

context = ProjectInspector(settings.workspace).inspect()
prompt = analysis_prompt("Crie uma API simples para gerenciar tarefas.", context.model_dump_json())
payload = {"model": "qwen3:8b", "messages": [{"role": "user", "content": prompt}], "stream": False, "think": False, "format": "json", "options": {"num_predict": 128}}
started = time.perf_counter()
try:
    response = httpx.post("http://localhost:11434/api/chat", json=payload, timeout=httpx.Timeout(connect=5, read=60, write=5, pool=5))
    data = response.json()
    print(json.dumps({"status": response.status_code, "seconds": round(time.perf_counter() - started, 2), "bytes": len(response.content), "prompt_chars": len(prompt), "metrics": {k: data.get(k) for k in ("done", "done_reason", "eval_count", "prompt_eval_count", "total_duration", "eval_duration")}, "content": data.get("message", {}).get("content", "")}, ensure_ascii=False))
except Exception as exc:
    print(json.dumps({"error": type(exc).__name__, "message": str(exc), "seconds": round(time.perf_counter() - started, 2), "prompt_chars": len(prompt)}))
