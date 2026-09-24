# Milestone 2.1 — Diagnóstico da integração Ollama

## Evidência diferencial

- `GET /api/tags`: HTTP 200 em aproximadamente 2,2 s; `qwen3:8b` listado.
- Chamada mínima `/api/chat`, sem `think:false`: não entregou resposta dentro de 15 s.
- Chamada antiga `teste_ollama.py`: excedeu 25 s sem concluir na primeira tentativa.
- `/api/generate`, `num_predict=16`, sem controle de thinking: HTTP 200 em 6,3 s, mas retornou `thinking`, `response` vazio e `done_reason=length`.
- `/api/chat` com `think:false`: HTTP 200 em 2,56 s para `OK`, `done_reason=stop`, content não vazio.
- `/api/chat` com `think:false` e `format=json`: HTTP 200 em 4,97 s para JSON válido.
- Prompt de análise de 834 caracteres com limite 128: 35,63 s, `eval_count=128`, `done_reason=length`, JSON truncado.
- Pipeline real após correção: `DONE`, 155,12 s, 1 task, 1 routing decision.

## Correções

`OllamaProvider` envia `think:false`, `format=json` apenas na chamada estruturada, `num_predict=384`, timeout padrão de 180 s, rejeita conteúdo vazio e registra métricas sem prompts. O parser possui reparo controlado para a resposta observada de task isolada. Nenhum código do modelo é executado.

## Limitações observadas

O hardware/modelo local pode levar mais de dois minutos para análise + planejamento. O modelo ocasionalmente retorna uma task sem o envelope do plano; o reparo é restrito e validado por Pydantic.

