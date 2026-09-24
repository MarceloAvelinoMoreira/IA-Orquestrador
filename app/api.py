from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db, init_db
from .engine import OrchestrationEngine
from .providers import OllamaProvider
from .schemas import AgentResponse, OrchestrationRequest, TaskCreate, TaskResponse
from .tasks import TaskManager

app = FastAPI(title=settings.app_name, version="0.1.0")
engine = OrchestrationEngine()

# The Vite development server runs on a separate origin during local use.
# Keep this limited to local development hosts; production deployments should
# replace it with their explicit frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def startup() -> None: init_db()


@app.get("/health")
def health() -> dict:
    engine.refresh_agent_health()
    provider = OllamaProvider()
    reachable = provider.health()
    agents_state = {a.name: a.status.lower() for a in engine.registry.all()} | {n: "not_configured" for n in ("gemini", "cursor")}
    return {"status": "ok" if reachable else "degraded", "service": settings.app_name, "database": "ok", "ollama": "ok" if reachable else "offline", "local_model": {"name": provider.model, "status": "available" if reachable else "unavailable"}, "agents": agents_state, "codex": {"status": engine.codex.status.lower(), "version": engine.codex.version}, "claude": {"status": engine.claude.status.lower(), "version": engine.claude.version}}


@app.get("/agents", response_model=list[AgentResponse])
def agents():
    return [AgentResponse(name=a.name, capabilities=list(a.capabilities), available=True) for a in engine.registry.all()]


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = TaskManager(db).create(payload)
    return TaskResponse(id=task.id, title=task.title, description=task.description, dependencies=payload.dependencies, status=task.status, agent=task.agent, result=task.result)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    manager = TaskManager(db)
    return [TaskResponse(id=t.id, title=t.title, description=t.description, dependencies=manager.dependencies(t), status=t.status, agent=t.agent, result=t.result) for t in manager.list()]


@app.post("/orchestrate")
def orchestrate(payload: OrchestrationRequest, db: Session = Depends(get_db)):
    if not payload.text: raise HTTPException(status_code=422, detail="request or objective is required")
    try:
        if payload.execution_mode in {"local", "mock"}:
            # Local Qwen question answering is deliberately independent from
            # external coding agents. It requires only Ollama on localhost.
            answer = engine.provider.chat(
                payload.text,
                system="Responda em português claro e útil. Não invente capacidades externas.",
            )
            return {
                "execution_id": None,
                "status": "DONE",
                "answer": answer,
                "final_response": answer,
                "agent": "qwen",
                "external_services": False,
            }
        # The browser uses local mode. The explicit test_mock mode remains
        # available for fast isolated tests without contacting Ollama.
        return engine.execute(payload, db=db, use_ollama=payload.execution_mode != "test_mock")
    except Exception as exc: raise HTTPException(status_code=502, detail=f"orchestration failed: {exc}") from exc
