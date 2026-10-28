# Ativação segura do Groq na Cloudflare

**Estado:** o código das integrações foi publicado em 28/10/2026. O código pode ser testado com mocks locais; não declarar integração real concluída até registrar a execução Cloudflare/Groq.

## Por que há duas credenciais?
- `GROQ_API_KEY`: segredo da API do provedor, **sempre no backend**.
- `FIO_DEMO_ACCESS_KEY`: senha de demonstração independente que protege o consumo da API por visitantes. Não é a chave Groq.
- O endpoint público continua disponível no modo **Simulado** sem senha. A BrasilAPI pode ser consultada com data completa, sem LLM.

## No painel Cloudflare

1. Abra **Workers & Pages → fio → Settings → Variables and Secrets**.
2. Confirme que `GROQ_API_KEY` foi cadastrado como **Secret** (não revelar nem copiar aqui).
3. Crie **outro Secret** chamado `FIO_DEMO_ACCESS_KEY`: gere no gerenciador de senhas uma sequência aleatória de **32 caracteres ou mais** (mínimo técnico de 24).
4. Salve o segredo e confira se a implantação foi atualizada. Não coloque o valor no GitHub, em prints ou logs.
5. Acesse a [demo](https://fio.erika-srcastro.workers.dev/), selecione **Groq real — acesso protegido** e informe **somente o código de demonstração** no campo da página.
6. Teste com dados fictícios; anote data, versão em `/healthz`, trace ID, decisão, tipo de percepção e resultado. Não publique conteúdo pessoal nem os valores dos Secrets.
7. Antes de enviar o código a terceiros, crie uma regra de *rate limiting* para `/api/chat` na Cloudflare e configure limites financeiros/usage no painel Groq.

## Testes esperados

| Caso | Resultado esperado |
|---|---|
| Usuário anônimo, modo simulado | Responde sem invocar Groq |
| Usuário anônimo, modo Groq | HTTP 403, sem chamada Groq |
| Código de demonstração inválido | HTTP 403 |
| Código de demonstração correto e chave Groq válida | Percepção `groq` e resposta controlada pelo Python |
| BrasilAPI data `20/11/2026` no modo simulado | Consulta HTTPS real à BrasilAPI |
| API externa indisponível | Mensagem de falha explícita; não inventar feriado |
| Solicitação de vigilância/punição | Resposta de limite, sem chamada LLM |

## Arquitetura e limitações

- Cloudflare Worker Python acessa Secrets via `self.env` e serviços externos via `fetch` assíncrono.
- A LLM **classifica intenção**, não executa ações e não altera contratos ou guardrails.
- Respostas do Groq são validadas pelo Pydantic; respostas inválidas geram fallback explícito.
- O app permanece **sem memória persistente** entre requisições.
- Logs técnicos registram `trace_id`, decisão, origem da interpretação, status da dependência e duração; não registram mensagens ou chaves.
- O código de demonstração ainda não é um sistema de autenticação de usuários. Para uso público contínuo, adicionar rate limiting, Cloudflare Access/Turnstile e armazenamento governado.
- `/healthz` informa `llm: locked` até os dois Secrets estarem disponíveis. `llm: protected` indica apenas **configuração**, não comprova chamada bem-sucedida.

## Fontes de referência

- Cloudflare Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Cloudflare Secrets: https://developers.cloudflare.com/workers/configuration/secrets/
- Cloudflare Python FFI: https://developers.cloudflare.com/workers/languages/python/ffi/
- Groq API: https://console.groq.com/docs/api-reference
