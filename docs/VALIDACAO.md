# Protocolo de validação e rastreabilidade

## Evidências mínimas por execução

- `test_id`, versão/commit, data e hora UTC, runtime e modelo/versão utilizados.
- Tipo: **mock local**, **requisição real de API** ou **interação real com LLM**.
- Entrada sanitizada e expectativa declarada antes da execução.
- Decisão, resposta, duração, status das dependências e resultado da rubrica.
- `trace_id` pseudonimizado, sem segredos nem dados pessoais no log.
- Evidência correspondente (captura, JSON ou arquivo de teste) e limitações da conclusão.

## Executar

~~~bash
uv sync
uv run python -m pytest -q
uv run python demo.py
uv run python demo_integracao.py
# Somente em ambiente com rede:
uv run python demo_api_real.py
# Somente com GROQ_API_KEY em variável de ambiente:
uv run python demo_groq.py
~~~

Critérios mínimos: resposta específica ou esclarecimento; respeito ao modo Full/Leve; nenhuma alegação de persistência; erros externos tratados sem alucinação; nenhuma exposição de credenciais.

**Atenção:** testes mockados não comprovam integração HTTP ou desempenho de LLM real. Repetições controladas e avaliação humana ainda são necessárias para estimar consistência.
