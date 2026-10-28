# Estado do projeto — 28/10/2026

| Componente | Situação | Evidência | Próximo passo |
| --- | --- | --- | --- |
| FIO v2, modos Full/Leve | Oito cenários individuais na Fase 2 | Capturas acadêmicas da Fase 2 | Avaliação de consistência em cenários novos |
| Motor Python v0.4.1 | Implementado e testado em CI | 51 testes aprovados em `cc37177d`, regressão Full/Leve | Ampliar evals para variações de contexto |
| BrasilAPI | **Integração real validada** | API-01, trace `2d46a92f-e7d0-4798-a017-59dade03fc1c` | Testar indisponibilidade e datas inválidas em produção |
| Groq | **Classificação real validada em interface** | API-02 e REG-01, trace IDs distintos | Medir custo, falhas e consistência |
| Cloudflare | **Worker 0.4.1 público e operacional** | `/healthz` verificado externamente e 3 screenshots | Endurecer acesso, tráfego e observabilidade |
| Full vs Leve com contexto parcial | **BUG-01 corrigido e revalidado** | REG-01: Full e Leve com mesmo contexto e respostas distintas | Monitorar regressões |
| Observabilidade | Trace ID e eventos técnicos categóricos no Worker | IDs exibidos no frontend e documentação | Implementar dashboards, retenção e métricas agregadas |

**O Worker atual admite mock e Groq protegido, e usa transporte HTTP assíncrono para a BrasilAPI. O modo Groq não deve ser divulgado sem rate limiting e controle de custos.**

**Escopo de validação:** a URL, versão e decisões com trace IDs foram verificadas; não houve auditoria dos logs internos Cloudflare, medições de custos ou testes de abuso. A evidência comprova cenários observados, não confiabilidade estatística.

### Evidências de produção e histórico

- [Registro de implantação e validação](EVIDENCIAS_CLOUDFLARE_2026-10-28.md).
- v0.3.2: primeira versão pública e teste de retomada simulada WEB-01.
- v0.4.0: API-01 BrasilAPI real; API-02 Groq real; detectado BUG-01 nos modos Full/Leve.
- v0.4.1: REG-01 confirma **respostas distintas** para Full e Leve com mesmo contexto e Groq real.
- 51 testes pytest aprovados no CI de correção: https://github.com/erikasrcastro/FIO/actions/runs/40707386497.

### Hardening de consumo e segurança (v0.5.0 — CI aprovado; implantação pendente)

O código contém Rate Limiting nativo Cloudflare (5 chamadas Groq/minuto por localidade, aproximado), fail-closed, Analytics Engine para eventos categóricos e tokens, 71 testes automatizados, e novos testes de abuso e autenticação. A conta Groq precisa de orçamento e alertas configurados separadamente pela responsável se o plano permitir. **Na última consulta externa, o domínio público ainda devolvia v0.4.1; portanto esses controles ainda não estavam verificados em produção.**

- [Plano de segurança e consumo](SEGURANCA_CONSUMO.md)
- [Evidências SG-01 e checklist](EVIDENCIAS_SEGURANCA_2026-10-28.md)
- [GitHub Actions — execução verde](https://github.com/erikasrcastro/FIO/actions/runs/40711170011)
