# FIO — evidências da implantação Cloudflare (28/10/2026)

## Ambiente

- URL: https://fio.erika-srcastro.workers.dev/
- Versão observada por consulta pública em `/healthz`: **`fio-worker-mvp-0.4.1`** (confirmada novamente após as capturas da proprietária).
- `/healthz`: `ok: true`, `llm: protected`, `session_memory: none`, `external_api: brasilapi_enabled`.
- O estado `protected` indica que o Worker reconhece a configuração dos dois Secrets. **Sozinho não prova uma chamada Groq**, mas os testes de interface API-02 e REG-01 exibem `Interpretação: groq` com respostas retornadas pelo backend.
- Chaves de API, senha de demonstração e outros segredos não constam desta evidência.

## WEB-01 — Retomada de tarefa via interface (versão 0.3.2)

- Execução real observada no formulário público em 28/10/2026.
- Contexto sintético: apresentação, slide 6, próximo passo confirmado.
- Decisão: `orientar_full`.
- Percepção: `mock`.
- Resposta: «Você estava em slide 6, resultados. Próxima ação: escrever a frase principal.»
- Trace ID: `65ff7102-cdfb-493c-9f7e-aaa93eb419b0`.
- Resultado: **aprovado** para renderização, chamada frontend-backend e retorno de trace.
- Limitação: não testou API externa nem Groq.

## API-01 — Consulta real BrasilAPI (versão 0.4.0)

- Execução pela interface pública do FIO em 28/10/2026.
- Provedor selecionado: Simulado — acesso livre. Modo de assistência: Full.
- Contexto sintético: tarefa «Planejamento de calendário acadêmico», parada «Calendário de novembro», próxima ação «Verificar data de feriado».
- Mensagem: «20/11/2026 é feriado nacional?».
- Resposta visível: «Segundo a BrasilAPI, 20/11/2026 consta como feriado nacional: Dia da consciência negra. Para planejar a retomada, você prefere manter ou rever essa data?»
- Decisão: `feriado_confirmado`.
- Interpretação: `rule`.
- Integração reportada pelo backend: `brasilapi`.
- Trace ID: `2d46a92f-e7d0-4798-a017-59dade03fc1c`.
- Erros visíveis: nenhum.
- Resultado: **aprovado** para fluxo end-to-end com BrasilAPI no Worker.
- Limite de evidência: o resultado foi verificado externamente pela interface e respectiva classificação da integração; não houve acesso aos logs internos da Cloudflare.

## API-02 — Groq real (usuária, 28/10/2026)

- **Executado e observado pela interface web**, com duas capturas: modo Full e Leve, mesmo contexto.
- Campo `Motor de interpretação`: `Groq real — acesso protegido`; credencial de demonstração informada pela proprietária. Nenhum valor secreto foi registrado.
- Tarefa: «finalizar o app fio»; ponto de parada: «configuração de secret»; próxima ação confirmada: **não preenchida**.
- Mensagem: «fui pegar agua e esqueci oq ue fazer agora».
- Ambos os resultados exibiram `Interpretação: groq` e `API externa: none` (none se refere à BrasilAPI, não ao Groq).
- Full: `Decisão: pedir_proximo_passo`; trace ID `a176a3fa-6293-47d0-9568-00d62f9b212e`.
- Leve: `Decisão: pedir_proximo_passo`; trace ID `2f70a78d-08d3-4846-8b98-d526bd562718`.
- Resposta idêntica nos dois modos: «Você estava em configuração de secret. Qual era a próxima ação concreta prevista nessa parte?».
- **Avaliação da integração Groq:** aprovada quanto a processamento autorizado, classificação e retorno; as duas capturas exibem `groq`. Não houve inspeção direta dos logs internos da Cloudflare.
- **Avaliação do comportamento Full/Leve:** reprovada na versão 0.4.0 quando falta o próximo passo; incidente **BUG-01**.

## BUG-01 — Full e Leve iguais com contexto parcial

- **Causa raiz verificada no código**: `FIOAgent._retomar()` verificava a ausência de `proximo_passo_confirmado` antes de consultar `modo`, levando ambas as modalidades à mesma ramificação `pedir_proximo_passo`.
- **Correção**: ramificação Full oferece microação explícita para reencontrar o ponto de parada sem supor ações anteriores; Leve oferece escolha contextual para preservar autonomia. Também foram diferenciadas as perguntas quando falta tarefa ou ponto de parada.
- **Teste de regressão**: `test_r03_regressao_print_full_leve_sem_proximo_passo` (reproduz o texto e a classificação Groq simulada) e `test_groq_full_vs_leve_without_confirmed_next_step` (caminho completo usando transporte Groq simulado).
- **CI**: 51 testes aprovados no GitHub Actions, execução https://github.com/erikasrcastro/FIO/actions/runs/40707386497.
- **Versão para validação pública**: `fio-worker-mvp-0.4.1`. O CI aprovado **não substitui** o teste real da implantação atualizada.
- **Evidência visual**: capturas apresentadas pela proprietária nesta conversa, não publicadas no repositório para evitar compartilhar imagens que contenham campos de credenciais, ainda que mascarados.
- **Comprovação posterior**: ver REG-01 abaixo. A validação em produção foi realizada pela proprietária e registrada por capturas com trace IDs distintos.

## REG-01 — Reteste do BUG-01 em produção, versão 0.4.1 (28/10/2026)

**Objetivo:** comprovar diferenciação Full/Leve no contexto incompleto, com autenticação autorizada e classificação Groq real.

**Ambiente verificado externamente:** `https://fio.erika-srcastro.workers.dev/healthz` devolveu `ok: true`, `version: fio-worker-mvp-0.4.1`, `llm: protected`, `session_memory: none`, `external_api: brasilapi_enabled`.

**Entrada idêntica nos dois cenários:**
- Tarefa: `finalizar o app fio`.
- Ponto de parada: `configuração de secret`.
- Próxima ação já definida: **vazio**.
- Mensagem: `não lembro o que tenho que fazer agora`.
- Motor: **Groq real — acesso protegido**. Credencial de demonstração mantida privada.
- Única variável alterada: modo `full` ou `leve`.

| Propriedade | Modo Full | Modo Leve |
|---|---|---|
| Versão | 0.4.1 | 0.4.1 |
| Decisão | `orientar_full_sem_passo` | `orientar_leve_sem_passo` |
| Interpretação | `groq` | `groq` |
| API complementar de dados | `nenhuma` | `nenhuma` |
| Trace ID | `358592be-8c7c-410e-9090-514189413512` | `b7134866-7fc3-4ef8-9d1a-3dfa0dbb2ed0` |

**Resposta Full:** «Na tarefa 'finalizar o app fio', você parou em 'configuração de secret'. Primeiro movimento: volte a essa parte e confira o último item concluído, sem alterar nada ainda. Assim você recupera o ponto de retomada.»

**Resposta Leve:** «Você parou em 'configuração de secret' na tarefa 'finalizar o app fio'. Prefere rever o que já concluiu ou identificar o que falta nessa etapa? Escolha só um desses caminhos.»

**Resultado:** **APROVADO**, com diferenciação observável dos modos, preservação de contexto fornecido e nenhuma afirmação inventada sobre próximo passo. Também validada a nova nomenclatura do painel `API de dados: nenhuma`, que não confunde uso de Groq com consumo da BrasilAPI.

**Limitações:** não foram inspecionados os logs internos do Worker ou métricas de custo do Groq, nem realizados testes de carga, latência percentil, abuso, resistência a prompt injection ou consistência estatística. O teste demonstra comportamento deste par de execuções, não garantia universal.

**Segurança da evidência:** três screenshots da proprietária foram examinados nesta conversa. Seus campos de credencial estão mascarados; não são republicados no repositório público por prudência. Foram persistidos somente os resultados técnicos e IDs não secretos.


## WEB-052 — Smoke test público após deploy 0.5.2 (28/10/2026)

**Procedimento:** preenchimento real da interface `https://fio.erika-srcastro.workers.dev/`, com dados inteiramente sintéticos, modo `Full` e percepção `mock`. Nenhuma credencial foi fornecida; Groq não foi selecionado.

- Tarefa: `Revisar documentação de teste`.
- Ponto de parada: `Seção de resultados`.
- Próximo passo confirmado: `Conferir o último item escrito`.
- Mensagem: `Fiz uma pausa e quero retomar`.
- Resposta: «Você estava em Seção de resultados. Próxima ação: Conferir o último item escrito.»
- Decisão: `orientar_full`.
- Interpretação: `mock`.
- API complementar: `nenhuma`.
- Trace ID: `278311a6-e682-408c-814a-73446d6fa493`.
- Erros visíveis: nenhum.
- **Resultado:** aprovado para processamento UI → backend → resposta contextual v0.5.2.
- **Limite de conclusão:** este teste não prova logs efetivamente persistidos, bloqueio HTTP 429, nem chamadas Groq reais na versão 0.5.2. Conferir o trace ID no painel Workers Logs para validar OBS-052.

## Conclusão provisória

O Worker **v0.5.2** foi confirmado em produção; o smoke test WEB-052 também passou usando interpretação simulada. A BrasilAPI foi consultada com sucesso anteriormente (API-01). A chamada Groq real e a diferenciação Full/Leve foram observadas pela interface. O BUG-01 está **resolvido e revalidado em produção** no REG-01, além dos 74 testes de CI aprovados na versão v0.5.2. Permanecem pendentes testes de limites/rate limiting, resiliência, carga e observabilidade operacional, antes de divulgar irrestritamente o acesso ao modo Groq.
