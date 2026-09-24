# Milestone 2 — Orquestração real com Qwen3 8B

O fluxo agora é `request → ProjectInspector → Qwen RequestAnalysis → Qwen PlanningOutput → validação Pydantic → grafo de dependências Python → Router → MockAgent → ValidationEngine → SQLite → FinalReport`.

O Qwen produz somente estruturas propostas. Python extrai JSON de respostas simples ou Markdown, valida schemas, normaliza IDs internos e verifica dependências inexistentes, auto-dependências e ciclos. Saída inválida recebe uma tentativa controlada adicional; falhas são reportadas como erro do provider.

O contexto do projeto é compacto e exclui `.venv`, `.git`, caches, `node_modules`, `dist` e `build`. O Router usa capacidades declaradas e status do agente. Apenas `MockAgent` está disponível; Codex, Claude, Gemini e Cursor permanecem `not_configured`.

## Testes

Testes normais usam mocks e não dependem do Ollama. Para integração local real: `\.venv\Scripts\python.exe scripts\test_local_orchestration.py`. Essa integração chama `qwen3:8b`, valida a estrutura retornada e não executa código gerado pelo modelo.

