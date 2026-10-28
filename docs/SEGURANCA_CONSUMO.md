# FIO — controles de consumo, telemetria e segurança (v0.5.0)

## Controles implementados no código (validar no deploy)

1. **Segredos**: `GROQ_API_KEY` e `FIO_DEMO_ACCESS_KEY` permanecem em Cloudflare Secrets. O código de demonstração deve ser guardado em gerenciador de senhas, separado da API key.
2. **Autorização**: segredo de demonstração comparado em tempo constante, antes de qualquer inferência Groq. Tentativas sem autenticação geram HTTP 403 sem chamada paga.
3. **Rate limiting**: binding `FIO_GROQ_RATE` (namespace `2026102807`), 5 solicitações/minuto por localidade da Cloudflare, chave agrupadora não secreta `fio-protected-groq-v1`. É **aproximado**, sujeito a sobrepassagem durante sincronização e **não é global**.
4. **Fail closed**: binding ausente ou com falha resulta em 503, rejeição 429 quando limite é excedido. O modo simulado permanece disponível.
5. **Chamadas Groq curtas**: modelo `openai/gpt-oss-20b`, saída máxima `350` tokens, timeout de rede de 12 s e saída JSON/Pydantic validada. Controles no backend; não são editáveis pelo visitante.
6. **Dados**: limitação de tamanho de entrada e corpo já existente. Não há memória entre requisições.
7. **Auditoria**: logs sem mensagens, credenciais ou IP. Analytics Engine `fio_usage_v1`: campos categóricos e tokens/latência, sem conversas, trace ID ou segredos.

## Limitações e próximas barreiras

**Não confundir 5 por minuto por localização com teto absoluto de gastos**. Cloudflare esclarece que o limitador é aproximado e local a cada data center; para cotas estritas globais, implementar Durable Objects. O limite de gastos da própria Groq é uma camada separada, disponível para contas pagas com permissão de proprietário da organização e sujeita a atualização de consumo com atraso.

**Ações manuais no painel Groq:**
- Em [Groq Console](https://console.groq.com/), abrir **Settings → Billing → Limits**, *se sua conta oferecer a função*.
- Configurar teto mensal conservador e alertas em 50%, 75% e 90%. O teto é **da organização**, não exclusivo do FIO. Não afirmar limite configurado sem verificar.
- Separar FIO em projeto da Groq com key própria se a funcionalidade estiver disponível; monitorar **Dashboard → Usage**.

**Ações manuais de Cloudflare:**
- Verificar deploy v0.5.0 e que ambos bindings aparecem no ambiente.
- Verificar a criação de `fio_usage_v1` em Workers Analytics Engine após um teste.
- Confirmar que requisições Groq bloqueadas retornam 429 e o modo mock permanece ativo.
- Adicionar uma regra WAF de proteção para `/api/chat` se o domínio/plano permitir, e considerar Cloudflare Access/Turnstile antes de distribuir a senha amplamente.

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
- https://console.groq.com/docs/spend-limits
