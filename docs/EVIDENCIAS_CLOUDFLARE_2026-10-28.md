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

## API-02 — Groq real

- Estado: **pendente de teste autorizado**.
- A interface dispõe da opção «Groq real — acesso protegido».
- Somente a proprietária deve utilizar `FIO_DEMO_ACCESS_KEY` no campo da interface.
- Teste sugerido: tarefa e ponto de parada fictícios, mensagem «Perdi o fio da apresentação. Pode me orientar?».
- Critérios para aprovar: percepção `groq`, decisão contextual, resposta segura, trace ID e ausência de erros.
- Em caso de falha: registrar o código/erro genérico e trace ID, **sem** compartilhar chaves.

## Conclusão provisória

O Worker 0.4.0 foi visto em produção e há evidência de uma consulta real ao serviço externo BrasilAPI. O Groq está configurado como protegido, mas não há evidência empírica de execução de inferência até concluir API-02. Não confundir CI de testes, endpoint saudável, segredos cadastrados e integração verificada.
