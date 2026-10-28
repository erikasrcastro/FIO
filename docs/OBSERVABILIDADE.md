# Observabilidade e rastreabilidade — contrato proposto

> **Estado:** o Worker já emite eventos categóricos com `trace_id` e tempo de processamento em logs. Ainda não há evidência de armazenamento, consultas estruturadas ou retenção configurada para esses logs. Este documento descreve a evolução planejada.

## Objetivo

Permitir acompanhar uma interação do início ao resultado, sem armazenar dados pessoais ou permitir que dados da LLM executem ações por conta própria.

## Identificadores

- `trace_id`: UUID aleatório por requisição, gerado no backend (não incluir e-mail, IP ou nome).
- `session_id`: identificador efêmero e pseudônimo; só quando necessário e com retenção definida.
- `version`: commit SHA curto ou tag implantada.
- `test_id`: ID imutável quando for execução da rubrica, como `T01` ou `R02`.

## Eventos recomendados

| Evento | Campos não sensíveis |
| --- | --- |
| `request.received` | trace_id, version, timestamp, modo, origem (web/teste) |
| `perception.completed` | intenção validada, confiança, duração_ms, provider, mock/real |
| `decision.selected` | contrato BC-01–BC-04, decisão, motivo categórico |
| `integration.called` | serviço, endpoint lógico, status HTTP, duração_ms, timeout |
| `response.sent` | decisão, duração_total_ms, categoria de resultado |
| `error.handled` | categoria, origem, fallback, sem conteúdo pessoal |

## Exemplo de trace sintético

~~~json
{
  "trace_id": "00000000-0000-4000-8000-000000000001",
  "version": "example-only",
  "test_id": "T02",
  "environment": "mock",
  "event": "decision.selected",
  "mode": "full",
  "decision": "pedir_contexto",
  "duration_ms": 4,
  "outcome": "expected"
}
~~~

## Indicadores iniciais

- Taxa de respostas válidas pela rubrica aplicável; separar mock, LLM real e usuários reais.
- Latência p50/p95 por etapa; indisponibilidade e timeout por provedor.
- Taxa de fallback seguro em caso de indisponibilidade externa.
- Violações de contratos, negativas de vigilância e alegações indevidas de memória.
- Número de consultas externas por sessão para limitar custo e abuso.

## Privacidade e limites

Não registrar prompts completos, respostas completas, tokens, chaves, IPs ou dados identificáveis em logs públicos. Preferir valores categóricos e trechos sintéticos. Aplicar redaction na origem. Definir prazo de retenção, políticas de acesso, limite de taxa e orçamento antes de abrir a demonstração.

## Critério de prontidão para disponibilizar ao professor

Exigir URL de demonstração, commit exato, testes de regressão aprovados, evidência real das APIs, `trace_id` retornado pela interface e logs correspondentes. Os resultados devem permitir reconstituir a **sequência técnica** sem recuperar conteúdo pessoal dos usuários.
