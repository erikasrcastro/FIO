# FIO — Manifesto de fechamento técnico e entrega FIAP, Fase 3

**Autoria:** Érika Francine Silva Rodrigues Castro — RM 574284. **Identificação documental anterior:** Grupo 36 na Fase 1 (não há confirmação de que o número do grupo permaneça igual na Fase 3). **Data da consolidação:** 28/10/2026.

## Síntese

O FIO é um assistente de retomada de tarefas baseado em contexto voluntariamente fornecido. Python valida e decide; Groq classifica intenção quando autorizado e necessário; a BrasilAPI fornece feriados nacionais sob demanda. O agente não observa a tela, não possui memória persistente, não diagnostica, não pune e não executa autonomamente outras aplicações. Os modos Full e Leve oferecem níveis distintos de orientação.

**Ambiente:** Python 3.13, Pydantic, Cloudflare Workers Free, Groq Free, BrasilAPI e GitHub Actions. **Orçamento autorizado:** R$ 0, sem plano pago, sem durable database e sem analytics pagos.

## Índice de artefatos verificáveis

| Artefato | Link | Função |
|---|---|---|
| Demonstração pública | https://fio.erika-srcastro.workers.dev/ | Interação web |
| Saúde do serviço | https://fio.erika-srcastro.workers.dev/healthz | Versão e bindings, não prova do fluxo completo |
| Código versionado | https://github.com/erikasrcastro/FIO | Fonte auditável |
| Relatório acadêmico | ENTREGA_FIAP_FASE3.md | Contexto, arquitetura, implementação, limites |
| Matriz EVAL-054 | EVALS_FIO_FASE3.md | Critérios de avaliação e casos |
| Protocolo | VALIDACAO.md | Tipos de teste e rubricas |
| Provas técnicas SEC-052/SEC-053 | EVIDENCIAS_SEGURANCA_2026-10-28.md | Testes HTTP e rastreios sem segredos |
| Registros de integração | EVIDENCIAS_CLOUDFLARE_2026-10-28.md | Groq e BrasilAPI |
| Plano de segurança Free | SEGURANCA_CONSUMO.md | Autorização e limites |
| Smoke test sem Groq | ../scripts/REG-054.ps1 | Regressão de produção |
| GitHub Actions | https://github.com/erikasrcastro/FIO/actions/workflows/tests.yml | Build e testes CI |

## Rastreabilidade por fase

- **Fase 1:** pacote PBL do FIO — Blueprint, System Prompt, Arquitetura, Relatório de Testes, Modelo de Estado, Registro de Alterações e manifesto LEIA-ME.pdf. A referência original do manifesto informa Grupo 36 e RM 574284.
- **Fase 2:** guardrails, prompting estruturado, memória, Evals, PromptOps e conceitos de RAG; as restrições do FIO foram preservadas.
- **Fase 3:** integração externa real, classificação Groq com controle de decisão Python, API BrasilAPI, tratamento de erros, rastreamento técnico, segurança de consumo, evidências de produção, Evals reproduzíveis.

## Gates de qualidade

| Gate | Condição para aprovação | Estado na elaboração |
|---|---|---|
| API-01 | BrasilAPI real respondeu com dado verificável | Aprovado em execução anterior |
| REG-01 | Groq Full e Leve produziram respostas diferentes | Aprovado em execução anterior |
| OBS-052 | Trace da interface correlacionado a Workers Logs | Aprovado |
| SEC-052 | Bloqueio do contador de produção Groq | Inconclusivo: seis HTTP 200/9s |
| SEC-053 | Bloqueio real do binding com contador independente, zero Groq | **Aprovado: sétima requisição HTTP 429/6,1s** |
| EVAL-054 | Matriz offline pytest e análise de limitações | A confirmar pelo CI do release |
| REG-054 | Rota de diagnóstico HTTP 404, UI, Full e Leve mock em produção | Pendente de publicação da versão v0.5.4 e smoke ao vivo |
| LOG-053 | Trace do SEC-053 localizado especificamente no painel Cloudflare | Pendente de consulta autenticada, sem acesso à conta nesta sessão |

## Principais resultados observados

Na versão v0.5.3, foram feitas 7 verificações autenticadas do limitador em 6,1s, todas com groq_called=False. A sétima retornou HTTP 429 e diagnostic_rate_limited; trace fe88ac72-a4c4-4739-a306-9c940856d096. Na versão v0.5.2, seis requisições Groq sequenciais retornaram HTTP 200 em 9s: esse resultado não prova bloqueio exato, pois o limitador da Cloudflare é aproximado e regional.

## Entrega e limites

A rota temporária SEC-053 está destinada à aposentadoria em v0.5.4 após a prova, preservando o histórico de resultados. O rate limiter não é uma cota global financeira rígida, e o produto continua sendo um MVP acadêmico sem armazenamento de dados pessoais nem certificação de segurança independente. Não alegar eficácia clínica nem observação automática.

**Validação acadêmica externa ainda necessária:** o manifesto localizado é explicitamente da Fase 1; a rubrica formal específica da entrega da Fase 3 não foi localizada entre os documentos desta pasta. Portanto, este pacote documenta tecnicamente os objetivos da fase, mas não presume requisitos institucionais ou grupo de submissão que não constem da fonte oficial.

## Check final

- [x] Evidência SEC-053 reproduzida e seus trace IDs preparados para arquivo permanente.
- [x] Sem chave Groq ou senha de demonstração em documentação.
- [x] Plano Free e limites explícitos.
- [ ] CI do release v0.5.4 concluído e confirmado.
- [ ] v0.5.4 implantada e rota temporária desabilitada.
- [ ] Smoke de produção REG-054.
- [ ] Correlação opcional com Workers Logs do trace SEC-053.
- [ ] Revisar rubrica específica da atividade antes da submissão institucional.

**Este documento é um manifesto técnico, não comprovação de submissão no portal da FIAP.**
