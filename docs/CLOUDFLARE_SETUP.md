# Execução Cloudflare Workers — FIO v0.5.2

**Ambiente público verificado:** https://fio.erika-srcastro.workers.dev/healthz. O endpoint respondeu com `version: fio-worker-mvp-0.5.2`, `llm: protected`, `groq_rate_limit: configured`, `usage_analytics: not_enabled` e `metrics_backend: workers_logs` em 28/10/2026.

## Configuração atual

- Repositório: `erikasrcastro/FIO`, branch `main`.
- Worker: `fio`, Python Workers via Pywrangler.
- Entrada: `worker.py`; ambiente em `wrangler.toml`.
- Deploy command: `uv run pywrangler deploy`; preview: `uv run pywrangler preview`.
- Segredos Cloudflare: `GROQ_API_KEY` (Groq Free) e `FIO_DEMO_ACCESS_KEY` (código de acesso da demo). Guardar valores exclusivamente no painel.
- Rate limit: binding `FIO_GROQ_RATE`, 5 requisições por 60 segundos por localidade (aproximado).
- Telemetria: Workers Logs Free ativados em `[observability]`. **Não** utiliza Analytics Engine.
- URLs: `/` para interface, `/healthz` para status e `POST /api/chat` para processamento.

## Etapas de implantação ou recuperação

1. Conectar repositório GitHub na Cloudflare e confirmar Worker de nome `fio`.
2. Manter `wrangler.toml` sob controle de versão e segredos separados da árvore pública.
3. Na integração Git, deixar Build command vazio, Deploy command `uv run pywrangler deploy` e Path `/`.
4. Em Cloudflare → Worker → **Settings → Variables and Secrets**, confirmar que os dois nomes de Secret existem, sem expor valores.
5. Em Deployments, verificar commit/resultado Ready. Abrir `/healthz` e conferir versão publicada.
6. No painel **Observability**, verificar pelo menos um evento técnico sem dados privados; validar Groq protegido e mock com entradas fictícias.
7. Em caso de falha, guardar trecho de log relevante e classificar: dependências, compatibilidade Pyodide, Secrets, bindings ou restrição do plano.

## Histórico e diagnóstico

- Primeira tentativa: `requirements.txt` incompatível com Pywrangler; dependências migraram para `pyproject.toml`.
- v0.3.2 e v0.4.1: aplicação e integrações reais exercitadas na Cloudflare.
- v0.5.1: falha `10089` porque `[[analytics_engine_datasets]]` requeria habilitar Analytics Engine na conta.
- v0.5.2: removido binding obrigatório Analytics Engine; `[observability] enabled=true` para Workers Logs Free. **Deploy verificado**, porém ainda não foi comprovado o comportamento 429 nem a presença dos eventos no painel.

## Segurança e custo

`GROQ_API_KEY` nunca vai para navegador, GitHub, logs ou prints. `FIO_DEMO_ACCESS_KEY` é um código compartilhado de avaliação, **não** autenticação individual. Dados enviados ao Groq devem ser fictícios. O projeto opera apenas em Cloudflare Workers Free e Groq Free, orçamento R$ 0. **Não autorizar upgrades ou recursos com custo**.

[Guia de ativação Groq](GROQ_ACTIVATION.md) · [Incidente 10089](INCIDENTE_BUILD_2026-10-28.md) · [Evidências](EVIDENCIAS_CLOUDFLARE_2026-10-28.md)
