# DEP-054 — Publicar e verificar o FIO v0.5.4 (sem serviços pagos)

**Situação:** código aprovado por CI e publicado no GitHub main. Em 28/10/2026, último GET público observado ainda respondeu v0.5.3. O deploy Cloudflare não foi realizado por esta automação.

## Etapa 1 — Cloudflare: publicação sem trocar de plano

O repositório principal usa Python Workers e o comando oficial já validado no projeto: `uv run pywrangler deploy`. O novo código não altera `wrangler.toml`, Secrets ou bindings. Se a integração Git do Worker publicar automaticamente, não há necessidade de rodar o comando; confirme primeiro a implantação atual.

No terminal do computador **dentro do clone local do repositório FIO**, com a conta Cloudflare autenticada e sem alterações locais não salvas:

```powershell
git status --short
git switch main
git pull --ff-only
uv run pywrangler deploy
```

Se `git status` indicar trabalho não salvo, interromper e preservar arquivos antes de atualizar. Se houver qualquer pedido para ativar Workers Paid, Analytics Engine ou recursos pagos, cancelar e não autorizar cobrança. Não copiar nem publicar os valores dos Secrets.

## Etapa 2 — verificar a versão, rota removida e regressão sem Groq

```powershell
(Invoke-RestMethod 'https://fio.erika-srcastro.workers.dev/healthz').version
```

Deve retornar `fio-worker-mvp-0.5.4`; `rate_diagnostic` deve ser `retired` e `groq_rate_limit` continuar `configured`.

```powershell
# No diretório do repositório atualizado:
& '.\scripts\REG-054.ps1'
```

O REG-054 confirma `GET /`, `GET /healthz`, rota temporária desativada (HTTP 404), mock Full e mock Leve. Não envia qualquer chave e não chama Groq.

## Etapa 3 — log histórico SEC-053 (consulta autenticada)

No painel Cloudflare, entrar no Worker `fio`, seção **Observability / Workers Logs** e filtrar pelo identificador:

`fe88ac72-a4c4-4739-a306-9c940856d096`

Esperado: evento `diagnostic_rate_limit`, decisão `diagnostic_rate_limited`, status `429`, `groq_called=false`, Worker v0.5.3. O UUID do FIO pode diferir do trace nativo da Cloudflare; pesquise pelo `trace_id` dentro da mensagem JSON impressa pelo aplicativo.

**Compartilhar somente** trace, evento, decisão, status, versão e `groq_called`; omitir chaves, dados da conta, cabeçalhos, conteúdo de mensagens e identificadores de pessoa. Se o evento tiver expirado ou não estiver acessível, registrar essa limitação, sem reexecutar rajada.

## Critérios de conclusão

- CI release v0.5.4: aprovado, 107 testes.
- SEC-053: aprovado no HTTP da execução original; log Cloudflare específico pendente.
- Publicação v0.5.4: pendente até `healthz` confirmar.
- REG-054 produção: pendente até saída de teste observada.
- SEC-052 Groq: inconclusivo, sem novas rajadas.
- Orçamento: R$ 0, somente Cloudflare Workers Free e Groq Free.
