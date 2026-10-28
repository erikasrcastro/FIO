# FIO — INC-002 | falha de deploy Cloudflare 10089

**Data:** 28/10/2026. **Serviço:** Worker `fio` em Cloudflare Workers Free. **Impacto:** o código da versão v0.5.1 não foi publicado; a implantação anterior v0.4.1 permaneceu operando.

## Evidência primária — log fornecido pela titular

O log mostra instalação bem-sucedida de Python e dependências, execução de `uv run pywrangler deploy`, upload pelo Wrangler 4.154.0 e reconhecimento dos dois bindings:

```text
Your Worker has access to the following bindings:
env.FIO_ANALYTICS (fio_usage_v1)        Analytics Engine Dataset
env.FIO_GROQ_RATE (5 requests/60s)      Rate Limit
env.FIO_ENV ("demo_mock")               Environment Variable

[ERROR] A request to the Cloudflare API (.../workers/scripts/fio/versions) failed.
You need to enable Analytics Engine. Head to the Cloudflare Dashboard to enable
[code: 10089]
Failed: error occurred while running deploy command
```

Não há evidência nesse log de erro de código Python, chave Groq, rate limiting nem necessidade de Workers Paid.

## Causa raiz

A versão v0.5.1 incluiu `[[analytics_engine_datasets]]` no `wrangler.toml` sem que o recurso Analytics Engine tivesse sido habilitado na conta. A API rejeitou a implantação com o código 10089.

## Correção v0.5.2, somente Free

1. Retirar o binding obrigatório `[[analytics_engine_datasets]]` do `wrangler.toml`.
2. Adicionar `[observability] enabled = true` para registros técnicos em **Workers Logs Free**.
3. Preservar `[[ratelimits]]`, o controle de acesso, o tratamento de HTTP 429 e as contagens de tokens nas mensagens de log sanitizadas.
4. Atualizar `/healthz`: `usage_analytics: not_enabled`, `metrics_backend: workers_logs`. Não interpretar `not_enabled` como falha da aplicação: é decisão explícita de custo zero.
5. Testes de regressão impedem reintrodução acidental do binding obrigatório antes de uma decisão da titular.

## Critérios de aceite

- [ ] GitHub Actions aprovado para a versão corrigida.
- [ ] Novo build da Cloudflare conclui como Ready, sem erro 10089.
- [ ] `/healthz` mostra `fio-worker-mvp-0.5.2` e `groq_rate_limit: configured`.
- [ ] Simulado Full/Leve responde corretamente.
- [ ] Modo Groq protegido funciona ou devolve falha segura, sem divulgar Secrets.
- [ ] Evento no painel de observabilidade, sem dados sensíveis.

**Princípio financeiro:** orçamento autorizado R$ 0. Nenhum upgrade foi solicitado ou autorizado. A configuração do Analytics Engine pode ser considerada depois, apenas se a responsável decidir habilitá-la sem cobrança.

Referências: https://developers.cloudflare.com/analytics/analytics-engine/pricing/ e https://developers.cloudflare.com/workers/observability/logs/workers-logs/
