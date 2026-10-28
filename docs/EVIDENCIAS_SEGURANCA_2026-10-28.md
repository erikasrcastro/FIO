# FIO — Security Gate SG-01 (28/10/2026)

## Escopo

Controles de custo e segurança sobre a integração Groq. Backend Python/Cloudflare e documentação em PT-BR. **Testes automatizados são distintos dos testes de implantação em produção.**

## Código entregue (v0.5.0)

- Cloudflare Rate Limiting binding `FIO_GROQ_RATE`: limite aproximado de **5 invocações por 60 segundos por localização Cloudflare**, mesma chave de contagem compartilhada para o código de acesso de demonstração.
- Autorização comparada em tempo constante **antes de consultar o rate limiter**. Se código inválido, HTTP 403 sem chamada Groq.
- Binding ausente ou erro ao avaliar a cota: HTTP 503 **fail-closed**, sem chamada Groq.
- Cota excedida: HTTP 429 e mensagem de alternativa via modo simulado.
- Classificador Groq não executa ferramentas; Pydantic valida os dados e Python determina a ação.
- Máximo de 350 tokens de saída configurados no modelo e timeout de rede configurado em 12 segundos.
- No código v0.5.1 havia binding `FIO_ANALYTICS`, mas o deploy foi **bloqueado com erro Cloudflare 10089** porque a conta não havia habilitado Analytics Engine. Na v0.5.2 o binding foi retirado, usando **Workers Logs Free** com contagem, latência, tokens e metadados categóricos sem conteúdo pessoal.
- Logs técnicos continuam incluindo `trace_id` e metadados operacionais, sem conteúdo da conversa.

## Evidências de testes

- GitHub Actions do código de segurança + correção de deploy v0.5.2: **74 testes aprovados**, execução https://github.com/erikasrcastro/FIO/actions/runs/40724281556. A implementação inicial contou 71 testes no run 40710884456.
- GitHub Actions do endpoint de saúde adicional: https://github.com/erikasrcastro/FIO/actions/runs/40711026257.
- Testes específicos: bloqueio de credencial, não execução de chamadas pagas se a credencial for inválida, cota estourada, binding ausente, exceção no limitador, resposta do limitador malformada, modo simulado sem Secret, bypass de regras determinísticas, injeção textual tentando acessar credenciais, validação dos tokens e não exposição das métricas no corpo de resposta.
- Limite de evidência: testes com limitador e transporte simulados, não ensaio de carga nem pentest.

## Verificação de produção (parcial — implantação v0.5.2 comprovada)

**Atualização de 28/10/2026:** o domínio https://fio.erika-srcastro.workers.dev/healthz **retorna v0.5.2** e informa presença do binding `FIO_GROQ_RATE`. A presença do binding não é prova do bloqueio HTTP 429; esse ensaio permanece pendente. **A inspeção dos logs agora está comprovada em OBS-052**, com o trace correlacionado à UI. Analytics Engine permanece intencionalmente desligado.

- [x] Confirmado em `/healthz`: `fio-worker-mvp-0.5.2`, `groq_rate_limit: configured`, `usage_analytics: not_enabled`, `metrics_backend: workers_logs`.
- [x] **OBS-052 aprovado:** evento JSON sanitizado foi encontrado no Workers Logs, correlacionado ao `trace_id` de WEB-052. Analytics Engine continua desativado.
- [ ] Efetuar uma chamada Groq com código privado e examinar contagem de tokens (sem publicar segredo).
- [ ] Fazer teste autorizado de limite com requisições sequenciais e demonstrar resposta 429; não efetuar teste de carga agressivo em produção.
- [x] **WEB-052 aprovado:** modo simulado Full respondeu em produção v0.5.2, sem credencial Groq.
- [x] Confirmado em 28/10/2026 com **duas capturas de tela**: **Groq Free — $0 — Current Plan** (plano atual indicado no painel Groq) e **Cloudflare Workers Free — Active** (Billing → Subscriptions da Cloudflare). A captura Cloudflare também mostrava o domínio em **Free Plan — Active**, sem método de pagamento cadastrado. O plano Developer da Groq aparece como categoria paga não contratada. **Orçamento autorizado: R$ 0**. Imagens fornecidas pela proprietária e analisadas nesta conversa; não republicadas no repositório público para evitar exposição de dados de conta.
- [ ] Validar teste offline Groq 429 e confirmar que não há retry automático.


## OBS-052 — Workers Logs Free: evento operacional confirmado em produção

**Data:** 28/10/2026, aproximadamente 13:44:38 BRT, conforme painel fornecido pela responsável. **Serviço:** `fio` / `POST /api/chat`. **Versão:** `fio-worker-mvp-0.5.2`.

O teste `WEB-052` enviou uma requisição sintética no modo **Full + mock**, recebeu orientação contextual e retornou `trace_id: 278311a6-e682-408c-814a-73446d6fa493`. A responsável localizou no painel Cloudflare **Observability → Workers Logs** o evento JSON personalizado correspondente, que continha:

```json
{
  "trace_id": "278311a6-e682-408c-814a-73446d6fa493",
  "event": "response",
  "decision": "orientar_full",
  "version": "fio-worker-mvp-0.5.2",
  "perception": "mock",
  "external": "none",
  "status": 200,
  "duration_ms": 0,
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "total_tokens": 0
}
```

Metadados Cloudflare relevantes, omitindo identificadores da conta: `scriptName: fio`, `eventType: fetch`, método `POST`, path `/api/chat`, `truncated: false`. O UUID da aplicação e o `$metadata.traceId` da Cloudflare são campos independentes, com valores diferentes; isso é esperado.

**Rubrica OBS-052: APROVADO.** O registro do Worker foi encontrado no ambiente e correlacionado com a resposta da UI. O conteúdo compartilhado não inclui a mensagem da pessoa, resposta textual, IP, código de demonstração ou chave Groq. Isto comprova esse evento; não constitui auditoria de todos os logs produzidos.

**Ressalva:** `duration_ms: 0` pode representar resolução ou localização do temporizador em Python/Workers; **não equivale à latência total medida na rede**. O valor exige ajuste futuro antes de uso como métrica de desempenho. Tokens 0 são esperados para o teste `mock` e não medem o consumo de uma inferência Groq real.

**Próximo gate:** `SEC-052` — verificar bloqueio efetivo pelo rate limiter no ambiente Cloudflare, sem testes de carga agressivos e mantendo apenas planos Free.

## Limitações do limitador e restrição Free

Cloudflare Rate Limiting é aproximado e regional. O orçamento aprovado do FIO é **R$ 0**: a conta deverá permanecer Cloudflare Workers Free + Analytics Engine Free + Groq Free. Não ativar Durable Objects pagos nem elevar os limites comerciais. Se Groq retornar 429 por limite do plano gratuito, responder com indisponibilidade temporária e modo simulado, sem tentar novamente automaticamente.

Referências:
- https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- https://developers.cloudflare.com/analytics/analytics-engine/pricing/
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/billing-faqs

## SEC-052 — Ensaio de limite Cloudflare em produção: inconclusivo

**Data:** 28/10/2026. **Worker:** v0.5.2. **Cenário:** script PowerShell SEC-052, provedor Groq, credencial autorizada, dados fictícios, chamadas sequenciais e sem retry. Valores dos Secrets não integram esta evidência.

| Tentativa | HTTP | Trace ID |
| --- | --- | --- |
| 1/6 | 200 | `2b35fb84-a199-4914-9392-b15c7da17049` |
| 2/6 | 200 | `09160e1c-fe55-4ce4-8f69-a9b63f092815` |
| 3/6 | 200 | `5be55449-f755-447e-b0d2-1a1d00e7941e` |
| 4/6 | 200 | `0b606f36-305a-4a6e-a97c-3c505bb1b056` |
| 5/6 | 200 | `7e6d1974-84a9-4c43-aefc-a0c2feeb0ce7` |
| 6/6 | 200 | `fa29806a-303a-418d-b169-a395ee95b340` |

**Duração total:** 9,0 segundos; **seis HTTP 200; nenhum HTTP 429**. Todas as seis requisições foram atendidas no caminho autorizado Groq do Worker; não há registro de consumo de tokens neste output.

**Veredito:** SEC-052 **INCONCLUSIVO**. Não é correto aprovar o bloqueio Cloudflare nem declarar falha definitiva apenas com este lote. A documentação oficial diz que a API de Rate Limiting é aproximada, regional e usa contadores eventualmente consistentes. Uma rajada pode ultrapassar 5/60s antes da sincronização: https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/.

**Decisão:** não repetir a rajada com chamadas Groq Free. Para avançar, propor um ensaio controlado da resposta do binding sem executar inferência da LLM, preservando acesso protegido, limite de chamadas baixo e nenhum serviço pago. A capacidade de cumprir um teto global rígido permanece não comprovada.

## SEC-053 — Endpoint de diagnóstico protegido criado

Versão de código v0.5.3 implementa `POST /api/diagnostics/rate-limit` autenticado pelo Secret demonstrativo existente. Usa `FIO_GROQ_RATE` com chave de contagem separada para não impactar o contador do Groq. Não faz chamadas LLM ou à BrasilAPI, e não ativa recursos pagos. Os testes locais cobrem auth, negação, falhas e isolamento. **Aguardar implantação e evidência do teste real; não marcar como aprovado ainda.** [Procedimento](SEC_053_RATE_DIAGNOSTIC.md).

## SEC-053 — Prova do binding isolado: APROVADO (28/10/2026)

**Ambiente:** Worker v0.5.3, rota protegida POST /api/diagnostics/rate-limit, mesma configuração do binding FIO_GROQ_RATE, contador separado do tráfego Groq. Script PowerShell SEC-053 executado com credencial apenas na máquina da responsável.

| Checagem | HTTP | code | trace_id |
|---|---|---|---|
| 1/12 | 200 | diagnostic_allowed | `6acd12ad-4648-4c49-90c3-9a317141739a` |
| 2/12 | 200 | diagnostic_allowed | `bd0467db-a958-40d9-ba17-a20bfc9e75de` |
| 3/12 | 200 | diagnostic_allowed | `0d022e7e-78eb-4e07-8009-2c4d6e2166ee` |
| 4/12 | 200 | diagnostic_allowed | `3d5e9a21-5dc4-4d3f-a4bf-a430ccbd769f` |
| 5/12 | 200 | diagnostic_allowed | `c63c1cd9-0fe1-4692-9075-a35a8ed2a2eb` |
| 6/12 | 200 | diagnostic_allowed | `c6362622-c0cb-4b52-8338-5af14f1d5f7d` |
| 7/12 | 429 | diagnostic_rate_limited | `fe88ac72-a4c4-4739-a306-9c940856d096` |

**Duração:** 6,1 segundos. **Permissões:** 6. **Bloqueio:** 1 (sétima solicitação). Em todas as respostas, groq_called=False. O script encerrou após a recusa HTTP 429.

**Veredito SEC-053:** APROVADO para a capacidade de o binding nativo Cloudflare recusar uma checagem em seu contador independente. **SEC-052 continua inconclusivo** para o tráfego real de Groq; a Cloudflare mantém contadores aproximados, locais e eventualmente consistentes.

**Privacidade:** não registrar valores de FIO_DEMO_ACCESS_KEY ou GROQ_API_KEY. O dado usado no ensaio é fictício, e nenhuma chamada ao Groq foi efetuada pelo endpoint de diagnóstico.

**Workers Logs:** não há leitura autenticada do evento SEC-053 disponível nesta sessão; correlacionar o trace da sétima tentativa com event=diagnostic_rate_limit, decision=diagnostic_rate_limited, status=429, groq_called=false, versão v0.5.3, sem mensagens ou credenciais. Até essa conferência, marcar correlação com o painel como PENDENTE, sem afetar a evidência da resposta HTTP.

**Encerramento posterior:** a rota temporária deve retornar HTTP 404 na v0.5.4; a evidência histórica fica neste documento. Não repetir rajadas.
