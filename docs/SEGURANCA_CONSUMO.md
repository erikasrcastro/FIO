# FIO — controles de consumo, telemetria e segurança (v0.5.0)

## Controles implementados no código (validar no deploy)

1. **Segredos**: `GROQ_API_KEY` e `FIO_DEMO_ACCESS_KEY` permanecem em Cloudflare Secrets. O código de demonstração deve ser guardado em gerenciador de senhas, separado da API key.
2. **Autorização**: segredo de demonstração comparado em tempo constante, antes de qualquer inferência Groq. Tentativas sem autenticação geram HTTP 403 sem chamada paga.
3. **Rate limiting**: binding `FIO_GROQ_RATE` (namespace `2026102807`), 5 solicitações/minuto por localidade da Cloudflare, chave agrupadora não secreta `fio-protected-groq-v1`. É **aproximado**, sujeito a sobrepassagem durante sincronização e **não é global**.
4. **Fail closed**: binding ausente ou com falha resulta em 503, rejeição 429 quando limite é excedido. O modo simulado permanece disponível.
5. **Chamadas Groq curtas**: modelo `openai/gpt-oss-20b`, saída máxima `350` tokens, timeout de rede de 12 s e saída JSON/Pydantic validada. Controles no backend; não são editáveis pelo visitante.
6. **Dados**: limitação de tamanho de entrada e corpo já existente. Não há memória entre requisições.
7. **Auditoria**: logs sem mensagens, credenciais ou IP. Analytics Engine `fio_usage_v1`: campos categóricos e tokens/latência, sem conversas, trace ID ou segredos.

## Política financeira obrigatória — somente Free, R$ 0

Decisão expressa em 28/10/2026: **usar exclusivamente Cloudflare Workers Free, Analytics Engine Free e Groq Free Plan**, sem adicionar forma de pagamento, fazer upgrade de plano ou utilizar componentes que exijam cobrança. Se um binding exigir plano pago, não habilitar a opção: permanecer na implantação anterior ou remover o recurso opcional.

**Limites informados pelos provedores em 28/10/2026:**
- Cloudflare Workers Free: 100.000 requisições/dia, até 10 ms de CPU por requisição. A franquia é da conta, não exclusiva do FIO.
- Cloudflare Analytics Engine Free: 100.000 pontos gravados e 10.000 consultas/dia. Verificar disponibilidade do binding no ambiente.
- Groq Free / `openai/gpt-oss-20b`: 30 RPM, 1.000 RPD, 8.000 TPM, 200.000 TPD — ver limites específicos da organização no painel.
- Ao atingir o Free Plan da Groq, o provedor devolve HTTP 429; o FIO repassa HTTP 429 com instrução para usar modo simulado, **sem nova tentativa automática**.
- No Free Plan do Groq não há cobrança pelo excesso: a solicitação é recusada. Não usar o Developer nem *Spend Limits*, que são funcionalidades associadas ao plano pago.
- O limitador Cloudflare (5 chamadas Groq/minuto por localidade) é aproximado e **não constitui cota global rígida**. Para esta demonstração acadêmica, não adotar Durable Objects pagos.
- O código não permite identificar se a conta dos provedores foi alterada para um plano pago. A proprietária deve verificar seus planos nos painéis; não afirmar que a conta foi auditada automaticamente.

**Operação no Free Plan:** manter o modo simulado sempre utilizável, tratar quota excedida como indisponibilidade temporária e conferir Usage e métricas sem exigir recursos pagos. Não compartilhar credencial de demonstração indiscriminadamente.

**Antes de liberar a versão 0.5.1:** validar `/healthz` e verificar que os bindings gratuitos funcionam. Caso uma ativação peça upgrade, cancelar a ativação e manter a versão 0.4.1 estável até adequarmos o projeto.

## Evals e testes

Os testes na suíte reproduzem: tentativa sem senha, injeção de prompt para expor segredos, ausência/falha do limitador, bloqueio após quota, exceções Groq, ausência de tokens, e isolamento de telemetria. São **testes offline simulados** e *não constituem* pentest, fuzzing, load test ou evidência da proteção em Cloudflare real.

## Queries exemplo — Analytics Engine

Não inclui informações pessoais; índices e campos permanecem categóricos.

```sql
SELECT
  blob4 AS perception,
  SUM(double1 * _sample_interval) AS requests,
  SUM(double3 * _sample_interval) AS prompt_tokens,
  SUM(double4 * _sample_interval) AS completion_tokens,
  SUM(double5 * _sample_interval) AS total_tokens
FROM fio_usage_v1
WHERE timestamp > NOW() - INTERVAL '24' HOUR
GROUP BY blob4
ORDER BY requests DESC;
```

```sql
SELECT blob2 AS decision, blob3 AS status,
  SUM(double1 * _sample_interval) AS requests
FROM fio_usage_v1
WHERE timestamp > NOW() - INTERVAL '1' HOUR
GROUP BY blob2, blob3
ORDER BY requests DESC;
```

**Cautela:** retornos `usage` ausentes são registrados como 0, mas isso não prova consumo zero.

## Documentação técnica

- https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- https://developers.cloudflare.com/analytics/analytics-engine/get-started/
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/billing-faqs
- https://developers.cloudflare.com/analytics/analytics-engine/pricing/
