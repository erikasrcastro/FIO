# FIO — Retomada inteligente de tarefas

[![Testes Python](https://github.com/erikasrcastro/FIO/actions/workflows/tests.yml/badge.svg)](https://github.com/erikasrcastro/FIO/actions/workflows/tests.yml)

**Um assistente de IA para ajudar pessoas a retomarem o que estavam fazendo, sem vigilância, culpa ou falsas promessas de memória.**

> Projeto acadêmico em evolução | FIAP — Tecnologia em Agentes Inteligentes | Grupo 16

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

O ponto de entrada `worker.py`, o `wrangler.toml` e a interface `web_ui.py` estão preparados para o **primeiro deploy de demonstração**. O Worker ainda não tem URL pública confirmada. Nesta etapa, a percepção é **simulada**; chamadas reais à Groq e BrasilAPI no Worker permanecem pendentes.

Use `uv run pywrangler dev` para desenvolvimento e `uv run pywrangler deploy` para publicação (somente após revisão). A configuração completa está em [CLOUDFLARE_SETUP.md](docs/CLOUDFLARE_SETUP.md).

## Execução local

Requisitos: Python 3.10 ou superior.

~~~bash
python -m pip install -r requirements.txt
python -m pytest -q
python demo.py
python demo_integracao.py
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

- **Fase 2:** oito cenários comportamentais documentados, cada um com uma execução; não demonstram consistência estatística.
- **Fase 3 — v3.1:** 29 testes locais aprovados em 28/10/2026; a integração externa foi testada com transporte simulado.
- **Ainda pendente:** executar e registrar chamadas reais às APIs, testar o modelo LLM conectado e realizar deploy público na Cloudflare.

Consulte [status](docs/STATUS.md), [arquitetura](docs/ARQUITETURA.md), [validação](docs/VALIDACAO.md), [observabilidade](docs/OBSERVABILIDADE.md) e [segurança](SECURITY.md).

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
