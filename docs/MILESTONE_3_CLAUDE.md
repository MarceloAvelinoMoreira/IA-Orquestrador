# Milestone 3B.1 — Claude Code

## Discovery and executable selection

Data da verificação: 2026-09-21.

- `where.exe claude`: nenhum executável encontrado.
- `claude --version`: comando inexistente.
- `claude --help`: comando inexistente.
- `claude auth status`: comando inexistente.

O launcher `%LOCALAPPDATA%\\pnpm\\claude.CMD` foi encontrado, mas falhou por incompatibilidade do binário. A descoberta percorre dinamicamente o pnpm store, valida cada candidato executando `--version` e seleciona o executável nativo `claude-code-win32-x64`. Resultado: versão `2.1.270 (Claude Code)`.

`auth status` retornou `loggedIn=true`, `authMethod=api_key` e `apiProvider=firstParty`. Nenhum segredo é registrado.

`ClaudeAgent` usa `-p`, `--output-format json`, `--input-format text`, `--restricted`, `--allowedTools Read,Edit`, `--no-session-persistence`, `shell=False`, workspace explícito e timeout próprio. Claude passa a ser reportado como `available` somente após health check real.

## Codex full E2E

O fluxo `POST /orchestrate` com `execution_mode=external` foi executado em `data/sandbox/e2e_codex_project`. Resultado: HTTP 200, `execution_id=EXEC-8a0f0d4763`, Router selecionou Codex, Codex alterou `calculator.py`, resultado foi persistido em SQLite e FinalReport foi produzido. A validação externa posterior do sandbox passou com `2 passed`.

## Teste real e bloqueio externo

O sandbox `data/sandbox/claude_test_project` foi preparado com `divide` deliberadamente incorreto. O Claude foi iniciado no sandbox, mas retornou `Credit balance is too low` em 3,08 s, sem modificar arquivos. O Pytest externo confirmou o estado inicial: 1 teste falhando (`16 == 4`).

Nenhuma permissão irrestrita foi habilitada e Git não foi inicializado. O E2E API Claude não foi executado porque o bloqueio de crédito impede validar edição real e seria incorreto declarar sucesso.
