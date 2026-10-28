# SEC-053 — Diagnóstico protegido da Cloudflare sem Groq

**Implementação:** v0.5.3, código no GitHub. **Teste real:** pendente até confirmar o deploy.

## O que valida

- Endpoint POST `/api/diagnostics/rate-limit`, protegido pelo Secret existente `FIO_DEMO_ACCESS_KEY`, enviado no cabeçalho `X-FIO-Demo-Key` (jamais usar a `GROQ_API_KEY`).
- Exatamente o **mesmo binding** de produção `FIO_GROQ_RATE` (configurado em 5/60s), porém com **chave de contagem distinta** da utilizada pelo Groq: `fio-rate-diagnostic-v1`.
- Nenhuma chamada Groq, BrasilAPI ou outro serviço externo. Não há nova assinatura, banco de dados nem binding pago.
- A autorização é verificada **antes** de consultar o limitador; a entrada obrigatória é JSON vazio `{}`.
- Log técnico estruturado (`event=diagnostic_rate_limit`) com trace ID, código e status, mas sem mensagens ou credenciais.

## Respostas possíveis

| Status | code | Significado |
| --- | --- | --- |
| 200 | diagnostic_allowed | O binding permitiu a checagem na chave de diagnóstico |
| 429 | diagnostic_rate_limited | O binding recusou a checagem na chave de diagnóstico |
| 403 | diagnostic_access_denied | Credencial incorreta; binding não é consultado |
| 503 | diagnostic_binding_unavailable / diagnostic_binding_invalid | Fail-closed: binding falhou ou devolveu resposta inválida |

Cada resposta válida inclui `groq_called: false` e `bucket: diagnostic_isolated`. Os resultados são classificados como **SEC-053**, não SEC-052: o ensaio anterior com Groq continua inconclusivo.

## PowerShell — ordem de execução

1. Confirme `https://fio.erika-srcastro.workers.dev/healthz` com versão `fio-worker-mvp-0.5.3` e `rate_diagnostic: protected_isolated`.
2. Copie o valor do Secret demonstrativo do seu gerenciador de senhas. **Não compartilhe aqui.**
3. No PowerShell, carregue a chave na variável segura, depois limpe a área de transferência.
4. Baixe o script do GitHub e **revise-o no Bloco de Notas antes de executar**.
5. Execute uma vez. No máximo 12 checagens sequenciais, com 900ms de pausa. Sem Groq.

~~~powershell
$FioDemoKey = ConvertTo-SecureString -String (Get-Clipboard -Raw).Trim() -AsPlainText -Force
$FioDemoKey.Length
Set-Clipboard -Value ""

$url = "https://raw.githubusercontent.com/erikasrcastro/FIO/main/scripts/SEC-053.ps1"
$arquivo = Join-Path $env:TEMP "SEC-053.ps1"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $arquivo
notepad $arquivo
& $arquivo -DemoAccessKey $FioDemoKey

$FioDemoKey.Dispose()
Remove-Variable FioDemoKey
~~~

O script confere a versão do Worker antes de qualquer POST: se a v0.5.3 não estiver ativa, não executa o teste. Se já carregou `$FioDemoKey` na sessão, não precisa carregá-la de novo.

## Resultado aceito

**SEC-053 aprovado:** observar HTTP 429 + `diagnostic_rate_limited` + `groq_called=False`. Se todas as 12 chamadas forem permitidas, registrar **inconclusivo**, não executar nova rajada. O Rate Limiting Cloudflare é aproximado e eventualmente consistente, por localização. Um bloqueio no contador de diagnóstico confirma o binding operacional, **não** prova limite global rígido nem que a cota Groq tenha sido estritamente protegida no SEC-052.

Depois conferir no Workers Logs o trace ID do evento de diagnóstico. **Orçamento autorizado: R$ 0, somente Free.**

Documentação oficial: https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
