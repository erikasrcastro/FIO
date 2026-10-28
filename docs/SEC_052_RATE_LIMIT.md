# SEC-052 — Teste controlado do Rate Limiting (v0.5.2)

**Situação: preparado, ainda não executado em produção.**

## Objetivo

Verificar se o binding FIO_GROQ_RATE, configurado para cinco verificações a cada 60 segundos por localização Cloudflare, produz HTTP 429 e o código groq_rate_limited antes de executar uma nova inferência.

O limite é **aproximado**, regional e de consistência eventual. Assim, seis respostas HTTP 200 consecutivas **não provam defeito nem sucesso**. Não executar grandes cargas nem repetir automaticamente.

## Procedimento

1. Conferir que o Worker público responde com versão 0.5.2 e groq_rate_limit: configured.
2. **Primeiro**, carregar o valor de FIO_DEMO_ACCESS_KEY no PowerShell com `$FioDemoKey = Read-Host 'Cole FIO_DEMO_ACCESS_KEY' -AsSecureString`. O valor é digitado de forma oculta e fica na variável SecureString, não no histórico de comandos. **Nunca** usar GROQ_API_KEY neste teste.
3. **Depois**, baixar e ler o script `scripts/SEC-052.ps1` deste repositório; executar com `& $arquivo -DemoAccessKey $FioDemoKey`.
4. Ele envia no máximo seis mensagens fictícias consecutivas por HTTPS ao Worker FIO. Não mostra ou salva a chave. Ao finalizar, descarte a variável com `$FioDemoKey.Dispose(); Remove-Variable FioDemoKey`.
5. Copiar só as linhas Tentativa / HTTP / code / trace_id e a duração, sem compartilhar chaves nem mensagens pessoais.

~~~powershell
# ETAPA 1 — carregar secret em memória; o prompt não mostra os caracteres
$FioDemoKey = Read-Host 'Cole o valor de FIO_DEMO_ACCESS_KEY' -AsSecureString

# ETAPA 2 — obter o script, revisar e executar
$url = 'https://raw.githubusercontent.com/erikasrcastro/FIO/main/scripts/SEC-052.ps1'
$arquivo = Join-Path $env:TEMP 'SEC-052.ps1'
Invoke-WebRequest -Uri $url -OutFile $arquivo
notepad $arquivo
& $arquivo -DemoAccessKey $FioDemoKey

# ETAPA 3 — limpar chave da sessão após o teste
$FioDemoKey.Dispose()
Remove-Variable FioDemoKey
~~~

## Interpretação

- HTTP 429 com code groq_rate_limited: **SEC-052 APROVADO** para o limite nativo Cloudflare. Correlacionar trace_id com Workers Logs.
- HTTP 429 com code groq_free_quota_exceeded: inconclusivo, pois a cota foi atingida no Groq.
- HTTP 429 sem código identificador: inconclusivo.
- HTTP 403: credencial de demonstração recusada; não prosseguir.
- HTTP 503: proteção fail closed ou falha no serviço; não prosseguir.
- Seis respostas HTTP 200: inconclusivo por eventual consistência, localidade ou tempo.
- Nenhuma repetição automática, nenhuma despesa autorizada, orçamento R$ 0.

A versão anterior OBS-052 já foi aprovada. O ensaio SEC-052 continua pendente até a proprietária enviar as saídas sanitizadas.

Fontes: https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/ e https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/invoke-webrequest.

## Ensaio realizado — 28/10/2026

A proprietária executou seis requisições autorizadas ao Groq pelo Worker v0.5.2, em 9 segundos. Todas retornaram HTTP 200; nenhum HTTP 429 foi observado. **SEC-052 permanece inconclusivo**, compatível com limites regionais aproximados e contadores eventualmente consistentes. Não repetir a bateria apenas para forçar bloqueio. A evidência integral dos seis trace IDs está registrada em EVIDENCIAS_SEGURANCA_2026-10-28.md.
