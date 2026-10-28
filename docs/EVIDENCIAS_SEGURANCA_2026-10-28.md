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
- `FIO_ANALYTICS`: dataset `fio_usage_v1`, com contagem, latência e tokens; não armazena mensagem, resposta do modelo, IP nem segredos.
- Logs técnicos continuam incluindo `trace_id` e metadados operacionais, sem conteúdo da conversa.

## Evidências de testes

- GitHub Actions da implementação principal: **71 testes aprovados**, execução https://github.com/erikasrcastro/FIO/actions/runs/40710884456.
- GitHub Actions do endpoint de saúde adicional: https://github.com/erikasrcastro/FIO/actions/runs/40711026257.
- Testes específicos: bloqueio de credencial, não execução de chamadas pagas se a credencial for inválida, cota estourada, binding ausente, exceção no limitador, resposta do limitador malformada, modo simulado sem Secret, bypass de regras determinísticas, injeção textual tentando acessar credenciais, validação dos tokens e não exposição das métricas no corpo de resposta.
- Limite de evidência: testes com limitador e transporte simulados, não ensaio de carga nem pentest.

## Verificação de produção (pendente)

No momento de escrita desta evidência o domínio https://fio.erika-srcastro.workers.dev/healthz **ainda retornava v0.4.1**, portanto não é correto declarar rate limiting / Analytics Engine efetivos em produção.

- [ ] Confirmar em `/healthz`: `fio-worker-mvp-0.5.1`, `groq_rate_limit: configured`, `usage_analytics: configured`.
- [ ] Confirmar um registro agregado em `fio_usage_v1` no painel Analytics Engine sem mensagens/credenciais.
- [ ] Efetuar uma chamada Groq com código privado e examinar contagem de tokens (sem publicar segredo).
- [ ] Fazer teste autorizado de limite com requisições sequenciais e demonstrar resposta 429; não efetuar teste de carga agressivo em produção.
- [ ] Verificar que modo simulado não foi bloqueado.
- [x] Confirmado pela proprietária em 28/10/2026: Groq no plano **Free** (declaração da titular) e Cloudflare com **Workers Free — Active** (captura de Billing → Subscriptions). A captura também mostrava o domínio no **Free Plan — Active**, sem método de pagamento cadastrado. Orçamento aprovado: **R$ 0**. A captura não foi incluída no repositório público para preservar detalhes da conta.
- [ ] Validar teste offline Groq 429 e confirmar que não há retry automático.

## Limitações do limitador e restrição Free

Cloudflare Rate Limiting é aproximado e regional. O orçamento aprovado do FIO é **R$ 0**: a conta deverá permanecer Cloudflare Workers Free + Analytics Engine Free + Groq Free. Não ativar Durable Objects pagos nem elevar os limites comerciais. Se Groq retornar 429 por limite do plano gratuito, responder com indisponibilidade temporária e modo simulado, sem tentar novamente automaticamente.

Referências:
- https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- https://developers.cloudflare.com/analytics/analytics-engine/pricing/
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/billing-faqs
