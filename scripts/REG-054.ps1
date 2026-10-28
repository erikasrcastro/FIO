# REG-054 - smoke test de producao, sem chave e sem Groq.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$base = 'https://fio.erika-srcastro.workers.dev'
$health = Invoke-RestMethod -UseBasicParsing -Uri "$base/healthz" -Method Get -TimeoutSec 15
if ($health.version -ne 'fio-worker-mvp-0.5.4') {
    Write-Host "DEPLOY PENDENTE: v0.5.4 nao publicada. Atual: $($health.version)."
    return
}
if ($health.rate_diagnostic -ne 'retired' -or $health.groq_rate_limit -ne 'configured') {
    throw 'Versao nova sem estado de seguranca esperado'
}
Write-Host 'REG-054 | v0.5.4 ativa e binding intacto.'

# A rota temporaria precisa ter desaparecido (GET: 404).
$status = 0
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri "$base/api/diagnostics/rate-limit" -Method Get -TimeoutSec 15
    $status = [int]$resp.StatusCode
} catch {
    try { $status = [int]$_.Exception.Response.StatusCode } catch {}
}
if ($status -ne 404) { throw "Rota de diagnostico ainda acessivel: HTTP $status" }
Write-Host 'Rota SEC-053 aposentada: HTTP 404.'

$page = Invoke-WebRequest -UseBasicParsing -Uri "$base/" -Method Get -TimeoutSec 15
if ([int]$page.StatusCode -ne 200 -or $page.Content -notmatch 'FIO') { throw 'UI publica nao respondeu como esperado' }
Write-Host 'UI publica: HTTP 200.'

$ctx = @{
    mode = 'full'
    provider = 'mock'
    task = 'Revisar relatorio ficticio'
    stop_point = 'Secao final'
    next_step = 'Conferir o ultimo paragrafo'
    message = 'Me ajuda a retomar'
} | ConvertTo-Json -Compress
$reply = Invoke-RestMethod -UseBasicParsing -Uri "$base/api/chat" -Method Post -ContentType 'application/json; charset=utf-8' -Body $ctx -TimeoutSec 15
if ($reply.decision -ne 'orientar_full' -or $reply.perception -ne 'mock' -or -not $reply.trace_id) {
    throw 'Mock Full: resposta inesperada'
}
Write-Host "Mock Full: OK. Trace=$($reply.trace_id)"

$ctx2 = @{
    mode = 'leve'
    provider = 'mock'
    task = 'Revisar relatorio ficticio'
    stop_point = 'Secao final'
    next_step = 'Conferir o ultimo paragrafo'
    message = 'Me ajuda a retomar'
} | ConvertTo-Json -Compress
$reply2 = Invoke-RestMethod -UseBasicParsing -Uri "$base/api/chat" -Method Post -ContentType 'application/json; charset=utf-8' -Body $ctx2 -TimeoutSec 15
if ($reply2.decision -ne 'orientar_leve' -or $reply2.perception -ne 'mock' -or -not $reply2.trace_id) {
    throw 'Mock Leve: resposta inesperada'
}
Write-Host "Mock Leve: OK. Trace=$($reply2.trace_id)"
Write-Host 'REG-054 aprovado: rota removida e fluxos mock Full/Leve preservados. 0 Groq.'
