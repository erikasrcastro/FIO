# Groq real protegido — operação do FIO

**Estado em 28/10/2026:** integração Groq real demonstrada em produção nas versões v0.4.0 e v0.4.1 com classificações retornadas pelo backend. Na v0.5.2, o Worker está online com `llm: protected` e Rate Limiting configurado; **uma inferência Groq pós-v0.5.2 ainda deve ser testada**.

## Dois segredos, duas funções

- `GROQ_API_KEY`: credencial do provedor, apenas no backend Cloudflare Secrets.
- `FIO_DEMO_ACCESS_KEY`: código de demonstração independente, que autoriza o modo Groq. Não é chave de provedor nem mecanismo de identidade de usuários.
- O navegador envia o código da demo no header `X-FIO-Demo-Key` ao próprio Worker; o Worker usa internamente a chave Groq.
- Modo mock e consulta BrasilAPI seguem disponíveis sem utilização da LLM (observadas as demais validações).

## Testar sem expor credenciais

1. Abrir https://fio.erika-srcastro.workers.dev/.
2. Escolher `Groq real — acesso protegido`.
3. Informar **somente** o código `FIO_DEMO_ACCESS_KEY` no campo indicado. Não colar `GROQ_API_KEY` na interface.
4. Preencher tarefa e ponto de parada **fictícios** e solicitar retomada.
5. Confirmar `Interpretação: groq`, decisão, modo e trace ID, sem enviar textos pessoais.
6. Com mesmo contexto e próxima ação vazia, comparar Full (microação explícita) e Leve (escolha orientada).

## Proteções e limites Free

- Rate limit aproximado de 5 chamadas Groq/60s por localidade da Cloudflare; exige confirmação do 429 em produção.
- Código incorreto → 403; indisponibilidade do limitador → 503; cota excedida no limitador ou Groq Free → 429.
- Se a Groq devolver 429, **não executar retry automático**; usar modo simulado. Nenhum upgrade é autorizado.
- Modelo: `openai/gpt-oss-20b` usado para **classificação de intenção**, nunca para execução irrestrita de ações.
- Pydantic valida o JSON da LLM; Python impõe regras e determina respostas.
- Não há memória persistente entre requisições, observação contínua de usuários nem leitura de tela.

## Cuidados para avaliadores

- Acesso Groq é destinado a testes autorizados, não a visitantes irrestritos; não publicar o código no GitHub ou slides.
- Verificar quotas no painel Groq Free. Se o limitador ou o provedor bloquear o teste, registrar erro/trace ID e utilizar mock.
- Logs técnicos e contagem de tokens são registrados em Workers Logs; verificar manualmente no painel Observability. Analytics Engine está desativado.
- Não confundir `llm: protected` no `/healthz` com prova de que o Groq respondeu a uma chamada naquela versão.

[Validação](VALIDACAO.md) · [Status](STATUS.md) · [Segurança e orçamento](SEGURANCA_CONSUMO.md)
