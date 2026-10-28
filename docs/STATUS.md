# Estado do projeto — 28/10/2026

| Componente | Situação | Evidência | Próximo passo |
| --- | --- | --- | --- |
| FIO v2, modos Full/Leve | Testado em oito cenários individuais | Capturas da Fase 2, fora deste repositório | Retestes independentes |
| Motor Python v3.1 | Implementado localmente | 29 testes pytest aprovados | Revisão em CI |
| BrasilAPI | Cliente implementado e testes mockados | Testes locais | Execução HTTP real |
| Groq | Adaptador implementado | Sem evidência de chamada real neste estágio | Execução com chave protegida |
| Cloudflare | URL pública do MVP v0.3.2 verificada em 28/10/2026 | GET /healthz e WEB-01 no modo mock confirmados | Validar novo deploy v0.4.0 e chamadas externas |
| Observabilidade | Especificada | Relatório de testes local | Traces redigidos e métricas com ambiente real |

**O Worker inicial utiliza percepção simulada e impede consultas BrasilAPI até existir transporte HTTP assíncrono testado.**

**Não afirmar deployment ou integração real como concluídos antes de apresentar URL, data, versão, logs saneados e evidência de execução.**

### Integrações v0.4.0

Backend Python e testes para chamadas BrasilAPI/Groq publicados; Groq requer Secret independente `FIO_DEMO_ACCESS_KEY`. **A existência do código e a aprovação do CI não constituem evidência de chamada remota real.** A validação em produção será registrada com versão, trace ID, horário UTC e ambiente. Guia: [GROQ_ACTIVATION](GROQ_ACTIVATION.md).
