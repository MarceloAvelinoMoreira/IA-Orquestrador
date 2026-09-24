# Milestone 3A — Codex Integration

## Discovery

Codex foi encontrado no PATH. Versão observada: `codex-cli 0.155.0-alpha.9.2`. `codex login status` confirmou autenticação ChatGPT sem registrar tokens. `codex exec --help` confirmou execução não interativa, `--cd`, `--sandbox`, `--json`, `--ephemeral` e timeout externo via subprocess.

## Integração

`CodexAgent` usa `subprocess.run` com lista de argumentos e `shell=False`. O prompt é um `TaskPacket` JSON contendo escopo explícito, workspace, critérios e validação. O modo externo é opt-in via `execution_mode=external`; o padrão continua `mock`.

## Segurança e sandbox

Execuções externas usam `--sandbox workspace-write`, `--approve-for-me`, `--skip-git-repo-check`, workspace explícito e escopo de arquivos. O projeto principal não é usado no primeiro E2E: `data/sandbox/codex_test_project` é separado. Git permanece não inicializado e não é criado automaticamente.

## Testes

Testes unitários não chamam Codex real. A integração real está em `scripts/test_codex_agent.py`; ela verifica health, registra snapshot, executa a task no sandbox, coleta arquivos alterados e produz relatório JSON. Codex, Claude, Gemini e Cursor não são tratados como disponíveis por mera existência de classe.

