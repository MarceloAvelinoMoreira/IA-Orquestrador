# IA Orquestrador

Sistema de orquestração local para Windows. O Milestone 2 usa o `qwen3:8b` para análise e planejamento estruturados, enquanto Python valida, cria tarefas, resolve dependências, roteia para o `MockAgent`, valida resultados e persiste o relatório.

## Executar

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

Configuração opcional via `.env`: `OLLAMA_URL`, `OLLAMA_MODEL`, `DATABASE_URL`, `ALLOW_COMMANDS` e `WORKSPACE`. Por segurança, `ALLOW_COMMANDS` é falso por padrão.

## Endpoints

- `GET /health` — estado da API e alcance do Ollama.
- `GET /agents` — agentes registrados.
- `GET /tasks` e `POST /tasks` — tarefas persistidas.
- `POST /orchestrate` — roteamento e execução da solicitação.

O fluxo detalhado está em `docs/MILESTONE_2.md`.

## Performance e inteligência

- Conexão HTTP persistente com Ollama para reduzir overhead entre chamadas.
- Cache curto de health checks dos agentes externos.
- Cache curto do contexto compacto do projeto.
- Normalização e inferência determinística de capabilities quando o Qwen usa aliases ou termos de domínio.
- Execução externa continua opt-in; o modo padrão permanece `mock`.

Codex externo é opt-in com `execution_mode=external`; o padrão conservador é `mock`. Consulte `docs/MILESTONE_3_CODEX.md`.

Claude Code foi encontrado dinamicamente no pnpm store, validado como versão 2.1.270 e autenticado. A execução real está bloqueada atualmente por `Credit balance is too low`. Consulte `docs/MILESTONE_3_CLAUDE.md`.

## Testes

Execute `\.venv\Scripts\python.exe -m pytest -q`.

## Interface neural

O frontend está em `frontend/` e usa apenas os endpoints reais existentes (`/health`, `/agents`, `/tasks` e `/orchestrate`). A atualização da atividade usa polling de 4 segundos; a visualização neural usa Canvas 2D com DPR limitado e reduz a densidade efetiva para funcionar como fallback em hardware mais modesto.

```powershell
cd C:\IA-Orquestrador\frontend
npm install
npm run dev
```

Com o FastAPI rodando em `http://127.0.0.1:8000`, abra `http://localhost:5173`. A API já permite CORS apenas para esses dois endereços locais.
