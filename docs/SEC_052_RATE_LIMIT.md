# SEC-052 — Teste controlado do Rate Limiting (v0.5.2)

**Situação: preparado, ainda não executado em produção.**

## Objetivo

Verificar se o binding FIO_GROQ_RATE, configurado para cinco verificações a cada 60 segundos por localização Cloudflare, produz HTTP 429 e o código groq_rate_limited antes de executar uma nova inferência.

O limite é **aproximado**, regional e de consistência eventual. Assim, seis respostas HTTP 200 consecutivas **não provam defeito nem sucesso**. Não executar grandes cargas nem repetir automaticamente.

## Procedimento

1. Conferir que o Worker público responde com versão 0.5.2 e groq_rate_limit: configured.
2. Baixar e ler o script scripts/SEC-052.ps1 deste repositório.
3. Executar no PowerShell do Windows. O script solicita apenas FIO_DEMO_ACCESS_KEY via Read-Host -AsSecureString; nunca fornecer GROQ_API_KEY.
4. Ele envia no máximo seis mensagens fictícias consecutivas, com a mesma chave de demonstração, por HTTPS ao Worker FIO.
5. Copiar só as linhas Tentativa / HTTP / code / trace_id e a duração, sem compartilhar chaves nem mensagens pessoais.

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
