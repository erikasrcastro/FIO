# FIO — evidências da implantação Cloudflare (28/10/2026)

## Ambiente

- URL: https://fio.erika-srcastro.workers.dev/
- Versão observada por consulta pública em `/healthz`: `fio-worker-mvp-0.4.0`.
- `/healthz`: `ok: true`, `llm: protected`, `session_memory: none`, `external_api: brasilapi_enabled`.
- O estado `protected` indica que o Worker reconhece a configuração dos dois Secrets. **Não comprova, por si só, uma chamada bem-sucedida ao Groq.**
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
- **Próxima comprovação**: `/healthz` na versão 0.4.1, repetir cenário Groq real em Full e Leve, capturar as duas decisões distintas e respectivos trace IDs.

## Conclusão provisória

O Worker 0.4.0 foi visto em produção; a BrasilAPI foi consultada e o Groq real retornou classificação pela interface web em duas modalidades. Foi descoberto o BUG-01 (mesma resposta Full/Leve com próximo passo ausente) e publicada a correção 0.4.1 no GitHub, com 51 testes aprovados. Ainda pendente: validação do deploy v0.4.1 com respostas Full/Leve distintas no ambiente Cloudflare.
