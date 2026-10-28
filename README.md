# FIO — Retomada inteligente de tarefas

[![Testes Python](https://github.com/erikasrcastro/FIO/actions/workflows/tests.yml/badge.svg)](https://github.com/erikasrcastro/FIO/actions/workflows/tests.yml)

**Um assistente de IA para ajudar pessoas a retomarem o que estavam fazendo, sem vigilância, culpa ou falsas promessas de memória.**

> Projeto acadêmico em evolução | FIAP — Tecnologia em Agentes Inteligentes | FIO: Grupo 36 na Fase 1 (confirmar identificação para a Fase 3)

## O problema

Uma interrupção pode fazer uma pessoa perder o ponto exato de uma tarefa. O FIO ajuda a reconstruir o contexto disponível e identificar **uma próxima ação executável**, sem assumir prioridades pelo usuário.

## Como funciona

- **Modo Full:** oferece orientação direta, com uma próxima ação específica quando existe contexto suficiente.
- **Modo Leve:** utiliza o mesmo contexto, mas estimula autonomia na definição do primeiro movimento.
- **Contexto insuficiente:** faz uma pergunta essencial por vez; não inventa tarefa, histórico ou ponto de parada.
- **Segurança:** não diagnostica, não monitora pessoas, não repreende e não alega memória persistente.
- **Integração externa opcional:** consulta feriados nacionais na BrasilAPI somente mediante pedido com data completa; informações externas não comandam o agente.

## Tecnologias

Python · Pydantic · pytest · Groq API (adaptador opcional) · BrasilAPI (consulta opcional)

## Demonstração web (Cloudflare Workers)

**Aplicação pública:** https://fio.erika-srcastro.workers.dev/ · [Health check](https://fio.erika-srcastro.workers.dev/healthz).

**Estado em 28/10/2026:** v0.5.2 está **online**. A integração real com BrasilAPI foi verificada (API-01) e a integração real Groq foi verificada com dois modos na v0.4.1 (API-02 e REG-01). Na v0.5.2, `/healthz` confirma o binding de limite e Workers Logs configurados; os testes operacionais de bloqueio 429 e do painel de logs ainda estão pendentes.

**[Comece pelo relatório acadêmico da Fase 3](docs/ENTREGA_FIAP_FASE3.md)**, depois [status](docs/STATUS.md), [arquitetura](docs/ARQUITETURA.md), [protocolo](docs/VALIDACAO.md) e [segurança](docs/SEGURANCA_CONSUMO.md).

Para publicar: `uv run pywrangler deploy`; para desenvolvimento local: `uv run pywrangler dev`. Não colocar `GROQ_API_KEY` nem `FIO_DEMO_ACCESS_KEY` no repositório. [Guia Cloudflare](docs/CLOUDFLARE_SETUP.md).

## Execução local

Requisitos para o projeto completo e Cloudflare Workers: Python 3.13 e [uv](https://docs.astral.sh/uv/).

~~~bash
uv sync
uv run python -m pytest -q
uv run python demo.py
uv run python demo_integracao.py
~~~

Os exemplos acima funcionam **sem rede**, usando um classificador de intenção e uma integração simulados. Para testar chamadas reais, consulte [o plano de validação](docs/VALIDACAO.md). A configuração de `GROQ_API_KEY` é necessária exclusivamente para a demo com LLM real; não coloque credenciais no Git.

## Contratos de comportamento

| Código | Contrato |
| --- | --- |
| BC-01 | Assistência adaptativa — Full versus Leve |
| BC-02 | Uma próxima ação contextualizada |
| BC-03 | Reconstrução segura, sem inventar histórico |
| BC-04 | Uso de dado externo apenas quando solicitado |

## Evidências e maturidade

- **Fase 2:** oito cenários individuais; não demonstram consistência estatística.
- **Fase 3:** chamadas reais à BrasilAPI e ao Groq no Worker, bug Full/Leve corrigido em produção, e CI com **74 testes aprovados**.
- **v0.5.2:** implantação online e bindings reconhecidos; aguardam comprovação operacional o HTTP 429 do limitador, os registros no painel Workers Logs e nova chamada Groq após o deploy.
- **Política financeira:** Groq Free e Workers Free confirmados pela responsável; orçamento R$ 0. Analytics Engine desligado.

Consulte o [relatório completo da Fase 3](docs/ENTREGA_FIAP_FASE3.md).

## Estrutura

~~~text
fio/           Núcleo Python, validação, decisão e integrações
tests/         Testes automatizados
docs/          Arquitetura, status, protocolo e evidências
demo*.py       Demonstrações locais e opcionais online
~~~

## Autoria

Projeto de Éricka Castro, desenvolvido no curso de Tecnologia em Agentes Inteligentes da FIAP.

**Nota:** repositório público não significa produto em produção nem autorização para processar informações sensíveis. Os resultados acadêmicos distinguem simulação, execução local e integração real.

## Segurança de consumo e métricas (v0.5.2)

O modelo Groq é protegido por `FIO_DEMO_ACCESS_KEY` e por um limitador nativo da Cloudflare de **5 chamadas/minuto por localidade de execução**, aplicado somente após validação da credencial e antes da chamada paga. Este limitador **não é uma cota financeira global rígida**: cada localização Cloudflare possui contagem aproximada. Se o binding faltar/falhar, chamadas Groq falham de forma segura; o modo simulado segue livre. Veja [plano de segurança e custos](docs/SEGURANCA_CONSUMO.md).

Métricas: **Workers Logs** (plano Free) com `trace_id`, decisão/status, latência e contagem de tokens declarada pela Groq. O envio para `fio_usage_v1` por **Analytics Engine está intencionalmente desligado**: o deploy anterior falhou com erro 10089 porque a função não estava ativada na conta Cloudflare. Nenhum conteúdo de mensagem, saída do modelo, IP ou segredo é impresso pelo aplicativo. Tokens ausentes não comprovam consumo gratuito. `/healthz` identifica `metrics_backend: workers_logs`.

## Somente Free — orçamento R$ 0 (decisão de 28/10/2026)

Projeto autorizado exclusivamente nos planos gratuitos de Cloudflare Workers e Groq; Analytics Engine está desativado. Não contratar Developer, Workers Paid, Durable Objects pagos ou serviços adicionais com faturamento. Ao atingir as cotas do Groq Free, devolver HTTP 429 e oferecer modo simulado, **sem retry automático ou upgrade**. O código não verifica o plano comercial da conta; conferir a categoria real no painel do provedor. Ver [política financeira](docs/SEGURANCA_CONSUMO.md).

### Recuperação de build Cloudflare — v0.5.2

A versão v0.5.1 não foi publicada porque a conta ainda não havia habilitado Analytics Engine (**Cloudflare 10089**). O Worker v0.5.2 remove `[[analytics_engine_datasets]]` do Wrangler e utiliza somente **Workers Logs Free**, preservando o limitador de requisições Groq. Em caso de pedido de upgrade, não habilitar plano pago. Evidência: [incidente de deploy](docs/INCIDENTE_BUILD_2026-10-28.md).
