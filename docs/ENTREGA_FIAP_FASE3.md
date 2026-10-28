# FIO — Relatório técnico para entrega acadêmica da Fase 3

**Curso:** Tecnologia em Agentes Inteligentes — FIAP.  
**Projeto:** FIO, assistente de retomada de tarefas interrompidas.  
**Responsável:** Éricka Castro.  
**Data do corte:** 28/10/2026.  
**Status:** demonstração pública do Worker v0.5.2 confirmada; validação integral dos controles novos pendente.  
**Grupo:** FIO identificado como **Grupo 36 na Fase 1**; confirmar se a submissão atual da Fase 3 usa o mesmo número.

## 1. Problema e objetivo

Interrupções podem causar perda do ponto de execução de uma tarefa. O FIO procura retomar o fluxo sem inventar contexto, vigiar pessoas ou impor prioridades. O contexto fornecido explicitamente pela pessoa (tarefa, ponto de parada, próximo passo confirmado e modo) limita a orientação.

## 2. Escopo técnico demonstrado

- Aplicação web pública hospedada em **Cloudflare Python Workers Free**.
- Backend **Python** orquestra entradas, validações, decisões e falhas.
- **Groq API** (`openai/gpt-oss-20b`) recebe o texto e contexto para classificar a intenção como JSON estruturado; Pydantic valida o retorno.
- **BrasilAPI** devolve dados oficiais expostos pela API para consulta de feriados nacionais quando o usuário pede uma data completa.
- Motor de decisão determinístico fornece respostas diferentes em **Full** e **Leve**; a LLM não executa ações arbitrárias.
- Cada requisição retorna `trace_id`; sem persistência de conversas. Mock permite demonstração mesmo sem Groq.
- Secrets privados e proteção de consumo mediante Cloudflare Rate Limiting aproximado 5/60s por localização.

## 3. Arquitetura e fluxo

Usuário → formulário (`/`) → Worker (`POST /api/chat`) → validação de entrada/contexto → regra (feriado/guardrails) ou classificação Groq protegida → validação Pydantic → decisão Python → resposta com `trace_id` → Workers Logs técnicos. O endpoint `/healthz` informa versão e bindings, mas não substitui testes de execução.

Veja [diagrama e contratos](ARQUITETURA.md).

## 4. Casos reais e evidências

| ID | Procedimento | Resultado |
| --- | --- | --- |
| WEB-01 | Retomada Full por interface mock | Aprovado, v0.3.2 |
| API-01 | Pergunta `20/11/2026 é feriado nacional?` | BrasilAPI real confirmou feriado, trace `2d46a92f-e7d0-4798-a017-59dade03fc1c` |
| API-02 | Classificação Groq real com senha demonstrativa | Integração confirmada na v0.4.0; revelou bug |
| BUG-01 | Mesmo contexto em Full e Leve com passo desconhecido | Respostas idênticas na v0.4.0; controlador corrigido |
| REG-01 | Repetição Full/Leve após correção | **Aprovado**, Groq real na v0.4.1, com respostas distintas |
| CI-74 | Testes Python no GitHub Actions | **74 aprovados** na execução [40724281556](https://github.com/erikasrcastro/FIO/actions/runs/40724281556) |
| DEP-052 | `/healthz` na URL pública v0.5.2 | **Aprovado** para implantação e presença dos bindings |
| WEB-052 | Retomada Full em v0.5.2 com percepção simulada | **Aprovado**, trace `278311a6-e682-408c-814a-73446d6fa493` |
| OBS-052 | Verificação de evento JSON com mesmo trace no Workers Logs | **Aprovado**; status 200, versão 0.5.2, sem dados da conversa |
| SEC-052 | Teste do bloqueio real por HTTP 429 | **Pendente** em produção |

Traces do teste REG-01: **Full** `358592be-8c7c-410e-9090-514189413512`; **Leve** `b7134866-7fc3-4ef8-9d1a-3dfa0dbb2ed0`. O contexto foi idêntico nos dois modos.

## 5. Segurança e decisões do projeto

- Sem diagnóstico, monitoramento de comportamento, alegações de memória permanente ou execução não autorizada.
- Credenciais `GROQ_API_KEY` e `FIO_DEMO_ACCESS_KEY` em Cloudflare Secrets; nunca em arquivos públicos.
- Dados recebidos de usuário/LLM/API são não confiáveis até validação; Python controla permissões e saída.
- **Custo autorizado: R$ 0.** Proprietária confirmou **Groq Free** e **Cloudflare Workers Free** com capturas privadas. Nenhum upgrade ou componente pago autorizado.
- Rate Limiting nativo por localização (não um teto global estrito) e política de bloqueio ao exceder quotas.
- Workers Logs Free sem mensagens pessoais ou segredos emitidos pelo código; Analytics Engine desativado na v0.5.2.

## 6. Registro de incidentes e melhorias

- **INC-001:** Pywrangler recusou `requirements.txt`; dependências foram migradas para `pyproject.toml`.
- **BUG-01:** Full/Leve não divergiam quando faltava o próximo passo; corrigido em v0.4.1 e validado com Groq real.
- **INC-002:** Cloudflare erro 10089 ao exigir habilitação do Analytics Engine em v0.5.1; corrigido em v0.5.2 removendo binding e utilizando Workers Logs Free.

Não ocultar esses incidentes: demonstram testes, identificação de causa raiz e regressão.

## 7. O que está pendente e o que não afirmamos

**Pendente:** testar HTTP 429 do binding na versão viva, repetir chamada Groq/BrasilAPI em v0.5.2, ampliar evals, verificar consistência com amostras repetidas e revisar a métrica de duração. **Observabilidade OBS-052 já foi comprovada:** o mesmo trace apareceu na interface e no Workers Logs da Cloudflare. `/healthz` sozinho não comprova execução real dessas funções na v0.5.2.

**Fora do escopo:** memória persistente, agente observando a tela, integração com agenda/arquivos de usuário, execução autônoma de tarefas ou autenticação individual. O FIO é um protótipo acadêmico funcional, não serviço clínico nem produto pronto para processamento de dados sensíveis.

## 8. Entregáveis e links

- **Demo pública:** https://fio.erika-srcastro.workers.dev/
- **Saúde do serviço:** https://fio.erika-srcastro.workers.dev/healthz
- **Repositório e código:** https://github.com/erikasrcastro/FIO
- **Arquitetura:** [ARQUITETURA.md](ARQUITETURA.md)
- **Validação:** [VALIDACAO.md](VALIDACAO.md)
- **Evidências de integração real:** [EVIDENCIAS_CLOUDFLARE_2026-10-28.md](EVIDENCIAS_CLOUDFLARE_2026-10-28.md)
- **Segurança e evidências:** [EVIDENCIAS_SEGURANCA_2026-10-28.md](EVIDENCIAS_SEGURANCA_2026-10-28.md)
- **Incidente:** [INCIDENTE_BUILD_2026-10-28.md](INCIDENTE_BUILD_2026-10-28.md)
- **Status:** [STATUS.md](STATUS.md)

## 9. Critérios de conclusão para submissão

- [x] Código-fonte público e controlado por versão.
- [x] LLM real e API complementar real demonstradas com rastreamento.
- [x] Python controla o fluxo e valida estruturas.
- [x] Dois modos distintos testados e bug corrigido.
- [x] Demo web pública e health check v0.5.2.
- [x] Testes automatizados no CI.
- [x] Documentação de segurança e restrição Free.
- [x] Evidência operacional de logs após v0.5.2 (OBS-052, trace correlacionado).
- [ ] Evidência operacional do rate limiter HTTP 429 (SEC-052).
- [ ] Revisão final conforme rubrica/roteiro exato da entrega FIAP da Fase 3.
