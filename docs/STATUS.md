# Estado verificado do projeto — 28/10/2026

**Produto:** FIO — agente de retomada de tarefas. **Repositório:** https://github.com/erikasrcastro/FIO. **Demo:** https://fio.erika-srcastro.workers.dev/.

## Matriz de prontidão

| Área | Estado factual | Evidência | Pendência |
| --- | --- | --- | --- |
| Interface e motor Python | Online, Worker **v0.5.2** | `/healthz` consultado externamente em 28/10 | Testes funcionais pós-release |
| LLM Groq | **Integração real validada na v0.4.1**; Secrets reconhecidos na v0.5.2 | API-02 / REG-01; `llm: protected` | Repetir chamada real na v0.5.2 |
| BrasilAPI | **Integração real validada** | API-01, trace `2d46a92f-e7d0-4798-a017-59dade03fc1c` | Falha externa em produção |
| Modos Full e Leve | **BUG-01 resolvido e retestado** | REG-01: orientações distintas com mesmo contexto | Amostra maior de evals |
| Testes | **74 aprovados** | https://github.com/erikasrcastro/FIO/actions/runs/40724281556 | Testes de carga, integração e consistência |
| Rate limiter | Configurado no Worker v0.5.2 | `groq_rate_limit: configured`; 5/60s por localidade | Confirmar bloqueio 429 no Worker real |
| Observabilidade | Workers Logs Free configurados | `metrics_backend: workers_logs` | Confirmar eventos no painel |
| Analytics Engine | **Não habilitado** por decisão Free | `usage_analytics: not_enabled` | Nenhuma ação obrigatória |
| Orçamento | **R$ 0**, Groq Free e Workers Free | Capturas privadas de ambas as assinaturas | Respeitar cotas |
| Memória | **Sem persistência** | `session_memory: none` | Não alegar memória durável |

## Registro cronológico e mudanças

- **v0.3.2:** primeiro deploy e frontend funcional (WEB-01).
- **v0.4.0:** chamadas reais Groq e BrasilAPI; BUG-01 identificado (Full e Leve iguais com próximo passo vazio).
- **v0.4.1:** BUG-01 corrigido e retestado em produção (REG-01).
- **v0.5.0–v0.5.1:** controles de consumo e testes; tentativa de deploy falhou por binding Analytics Engine não ativado (INC-002, Cloudflare 10089).
- **v0.5.2:** configuração simplificada sem Analytics Engine; deploy público confirmado e endpoints indicam Rate Limiting e Workers Logs habilitados. CI: 74 testes aprovados.

## Limites das afirmações

`llm: protected` prova que os dois Secrets são reconhecidos, **não** que a versão atual tenha feito uma inferência real. `groq_rate_limit: configured` prova presença do binding, **não** aplicação da cota em teste de produção. `metrics_backend: workers_logs` identifica configuração, **não** comprova que o painel recebeu um evento. Não extrapolar resultados mockados para operação real.

## Arquivos canônicos

- [Entrega FIAP Fase 3](ENTREGA_FIAP_FASE3.md)
- [Arquitetura](ARQUITETURA.md)
- [Protocolo de validação](VALIDACAO.md)
- [Evidências de produção](EVIDENCIAS_CLOUDFLARE_2026-10-28.md)
- [Evidências de segurança](EVIDENCIAS_SEGURANCA_2026-10-28.md)
- [Incidente e correção](INCIDENTE_BUILD_2026-10-28.md)
- [Segurança e política Free](SEGURANCA_CONSUMO.md)
