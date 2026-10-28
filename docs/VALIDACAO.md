# Validação e Evals do FIO — Fase 3

## Tipos de prova (não intercambiáveis)

1. **Teste automatizado local/CI:** valida contratos e regras em ambiente controlado; dependências podem estar simuladas.
2. **Chamada real a uma API:** demonstra comunicação externa HTTP com dado devolvido pelo provedor.
3. **Teste end-to-end da UI:** demonstra interface, backend, integração e saída observada.
4. **Operação/observabilidade:** comprova registros técnicos no ambiente, além do resultado da UI.
5. **Avaliação de consistência:** requer repetição suficiente para detectar respostas instáveis; casos isolados não estimam taxa de acerto universal.

## Requisitos mínimos por evidência

`test_id`, objetivo, data (UTC e fuso quando aplicável), ambiente, versão/commit, provedor (mock/Groq/BrasilAPI), entrada sintética, resposta/decisão, HTTP status se disponível, `trace_id`, esperado vs observado, avaliação e limitações. Nunca incluir `GROQ_API_KEY`, `FIO_DEMO_ACCESS_KEY`, mensagens pessoais ou dados não autorizados.

## Resultados confirmados

| Teste | Ambiente | Resultado observado | Status |
| --- | --- | --- | --- |
| WEB-01 | Worker v0.3.2 | Retomada Full via interface com trace | Aprovado |
| API-01 | Worker v0.4.0 | Consulta BrasilAPI 20/11/2026 → feriado nacional, trace `2d46a92f-e7d0-4798-a017-59dade03fc1c` | Aprovado |
| API-02 | Worker v0.4.0 | `perception: groq` com código válido, mesma resposta Full/Leve | **Integração aprovada; BUG-01 aberto** |
| REG-01 | Worker v0.4.1 | Full `orientar_full_sem_passo` ≠ Leve `orientar_leve_sem_passo` | Aprovado; BUG-01 encerrado |
| CI-74 | GitHub Python 3.13 | 74 testes passaram, run 40724281556 | Aprovado |
| DEP-052 | Worker v0.5.2 | `/healthz` com `ok: true` e bindings reconhecidos | Aprovado apenas para implantação/configuração |
| WEB-052 | Worker v0.5.2 | Interface mock Full retornou `orientar_full`, trace `278311a6-e682-408c-814a-73446d6fa493` | Aprovado |
| OBS-052 | Worker v0.5.2 | Log real com o mesmo trace, `status: 200`, `truncated: false`, sem mensagem/credenciais no evento | **Aprovado** |
| SEC-052 | Worker v0.5.2 | Bloqueio HTTP 429 em produção | **Pendente** |

Consulte [o histórico completo de evidências](EVIDENCIAS_CLOUDFLARE_2026-10-28.md) e [evidências de segurança](EVIDENCIAS_SEGURANCA_2026-10-28.md).

## Procedimento de teste local

```bash
uv sync
uv run python -m pytest -q
uv run python demo.py
uv run python demo_integracao.py
```

Para testes locais com rede, executar `uv run python demo_api_real.py`; para Groq, usar `uv run python demo_groq.py` com variável de ambiente privada. O worker público usa `POST /api/chat` em JSON; só selecionar Groq protegido com código de demonstração, nunca com a chave do provedor.

## Checklist de segurança da operação

- Validar JSON, tipos, limites de comprimento e campos.
- Auth: código Groq demonstrativo não deve ser exposto, logado ou publicado.
- Rate limiting: limite Cloudflare aproximado 5/60s por localidade, não limite mundial rígido.
- API externa: timeout, fallback e ausência de alucinação.
- Groq: usar intenção estruturada validada, sem autorização para execução livre.
- Memória: nenhuma persistência entre requisições, não anunciar recuperação de conversas antigas.
- Logs: registrar apenas metadados categóricos e tokens/latência, nunca conteúdo da conversa.
- Sem dados pessoais/sensíveis; orçamento autorizado R$ 0 e apenas planos Free.

## Próximos testes de aceite

- **SEC-052:** 429 real sob cota por localidade; sem repetição automática e mock intacto.
- **OBS-052 (concluído):** evento JSON confirmado na Cloudflare, correlacionado à UI. `duration_ms=0` exige investigação futura.
- **EVAL-052:** cenários de contexto ausente/parcial/completo, vigilância, diagnóstico, injeção de prompt, API indisponível; 3–5 repetições conforme custo disponível, com rubrica humana.
- **DEP-052b:** confirmar que Groq e BrasilAPI seguem funcionando com runtime v0.5.2.

**Critério final:** OBS-052 já foi aprovado; não declarar SG-01 concluído sem SEC-052 (429 real) e revalidação Groq na 0.5.2. Nenhum teste de carga agressivo em ambiente Free.
