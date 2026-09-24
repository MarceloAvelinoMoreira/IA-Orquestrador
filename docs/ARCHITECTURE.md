# Arquitetura — Milestones 1 e 2

`main.py` expõe a aplicação FastAPI em `app.api`. A camada API usa `schemas.py`, `TaskManager` e SQLAlchemy (`db.py`/`models.py`) para persistir tarefas no SQLite. `OrchestrationEngine` coordena `Router`, `AgentRegistry`/`BaseAgent`/`MockAgent` e `OllamaProvider`.

As operações locais estão separadas em `CommandRunner`, `SecurityLayer`, `GitManager` e `ValidationEngine`. Comandos são desabilitados por padrão e comandos potencialmente destrutivos são bloqueados. O Router aplica scoring determinístico sobre capacidades do agente; o provider usa `/api/tags` e `/api/chat` do Ollama.

No Milestone 2, `OrchestrationEngine` coordena `ProjectInspector`, `RequestAnalysis`, `PlanningOutput`, parser estruturado, grafo determinístico, Router por capabilities, MockAgent, ValidationEngine e `FinalReport`. Cada execução recebe `execution_id` e é persistida em `orchestrations`. O Git não estava inicializado (`UNVERIFIED`). A disponibilidade do Ollama e do modelo é reportada dinamicamente por `/health`.

Milestone 3A adiciona `CodexAgent` real, opt-in, com TaskPacket, subprocesso seguro, sandbox workspace-write, timeout separado, captura JSONL e escopo explícito. `MockAgent` continua padrão para testes e fallback.

Claude Code é descoberto por candidatos do PATH/launcher/pnpm store e validado por execução de `--version`; o launcher incompatível é rejeitado. `ClaudeAgent` usa execução restrita e permanece sujeito à disponibilidade real de créditos.
