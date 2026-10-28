# Roadmap do FIO — progresso real e próximos gates

Atualizado em **28/10/2026**. Estados baseados no GitHub, CI e execução pública, não em funcionalidades presumidas.

| Marco | Estado | Evidência |
| --- | --- | --- |
| Identidade, guardrails e dois modos | **Concluído no MVP** | Testes Fase 2; REG-01 em produção com Full ≠ Leve |
| API externa real (BrasilAPI) | **Validado em produção** | API-01, trace `2d46a92f-e7d0-4798-a017-59dade03fc1c` |
| LLM Groq integrada à decisão Python | **Validado em produção na v0.4.1** | API-02, REG-01; `perception: groq` |
| UI pública e backend em Cloudflare | **v0.5.3 comprovada; v0.5.4 em release** | SEC-053 passou em produção; CI 107 testes para v0.5.4 |
| Testes automatizados | **107 aprovados** | GitHub Actions `40783617792`, release v0.5.4 |
| Secrets e controle de acesso à demo Groq | **Configurados e uso anterior validado** | Capturas Groq real e `llm: protected` |
| Rate limiting nativo | **SEC-053 aprovado, SEC-052 inconclusivo** | 7 checks isolados/6,1s, sétima HTTP 429; sem chamada Groq |
| Workers Logs | **OBS-052 validado em produção** | Log JSON encontrado com trace `278311a6-e682-408c-814a-73446d6fa493` e HTTP 200 |
| Recuperação de falhas externas | **Testada em mocks** | pytest; cenários reais de falha controlada **pendentes** |
| Segurança ofensiva e consistência | **Parcial** | Casos automatizados; sem pentest, sem estudo estatístico |
| Pacote FIAP Fase 3 | **Em atualização** | [entrega consolidada](ENTREGA_FIAP_FASE3.md) |

## Próximos gates sem custos

1. **OPS-01 (concluído):** evento JSON no Workers Logs correlacionado ao trace da UI, sem mensagens nem Secrets. Revisar `duration_ms=0` numa melhoria futura.
2. **SEC-02 / SEC-053 (encerrado quanto ao binding):** 429 confirmado em contador isolado, zero Groq; não repetir rajadas. SEC-052 específico Groq inconclusivo.
3. **EVAL-02:** repetir cenários Full/Leve com contexto ausente, incompleto e completo; registrar variabilidade, guardrails, erros e avaliação humana.
4. **FIAP-03:** organizar link, commit de referência, relatório técnico, vídeo ou imagens permitidas, testes e limitações, mantendo todos os entregáveis em PT-BR.
5. **Futuro (fora do escopo obrigatório):** conversação multi-turno por sessão consentida, melhorias de acessibilidade, cota global rígida apenas se houver opção gratuita comprovada.

**Não implementado:** monitoramento contínuo do usuário, memória persistente, execução autônoma em aplicativos, leitura de tela ou priorização automática. Não sugerir essas capacidades como se já existissem.

## Preparação do release v0.5.4

A rota temporária de diagnóstico foi retirada do Worker; EVAL-054 foi incorporada aos testes e a BrasilAPI ganhou proteção adicional contra nomes externos com comandos explícitos. CI: 107 testes verdes. Faltam deploy público e smoke REG-054; correlação com Workers Logs SEC-053 e conferência de rubrica FIAP permanecem verificações externas.
