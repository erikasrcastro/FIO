# SEC-053 | Diagnostico autenticado do binding Rate Limit SEM Groq (PowerShell 5.1 ou 7).
# Maximo 12 checagens, sem chamada LLM ou BrasilAPI; sem imprimir ou salvar segredos.
param(
    [Parameter(Mandatory = $true)]
    [System.Security.SecureString]$DemoAccessKey
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$baseUrl = 'https://fio.erika-srcastro.workers.dev'
$uri = "$baseUrl/api/diagnostics/rate-limit"
$maxRequests = 12
$secret = $DemoAccessKey
$ptr = [IntPtr]::Zero
$plainCode = $null
$previousProgress = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
try {
    # Nao executar ensaio se a versao nova ainda nao estiver em producao.
    $health = Invoke-RestMethod -UseBasicParsing -Uri "$baseUrl/healthz" -Method Get -TimeoutSec 15
    if ($health.version -ne 'fio-worker-mvp-0.5.3' -or
        $health.rate_diagnostic -ne 'protected_isolated' -or
        $health.groq_rate_limit -ne 'configured') {
        Write-Host ("Aguardando v0.5.3. Versao atual: {0}; nenhum teste executado." -f $health.version)
        return
    }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $plainCode = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    if ([string]::IsNullOrWhiteSpace($plainCode) -or $plainCode.Length -lt 24) {
        Write-Host 'Codigo invalido. Nenhum pedido enviado.'
        return
    }
    $payload = '{}'
    Write-Host 'SEC-053 | binding real com bucket isolado; ZERO chamadas Groq.'
    Write-Host 'No maximo 12 checagens. Sem retries automaticos.'
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $approved = $false
    for ($i = 1; $i -le $maxRequests; $i++) {
        $status = 0
        $responseText = ''
        try {
            $params = @{
                Uri = $uri
                Method = 'Post'
                UseBasicParsing = $true
                TimeoutSec = 18
                ContentType = 'application/json; charset=utf-8'
                Headers = @{ 'X-FIO-Demo-Key' = $plainCode }
                Body = $payload
                ErrorAction = 'Stop'
            }
            $result = Invoke-WebRequest @params
            $status = [int]$result.StatusCode
            $responseText = [string]$result.Content
        } catch {
            $webError = $_
            $responseObj = $null
            try { $responseObj = $webError.Exception.Response } catch {}
            if ($null -ne $responseObj) {
                try { $status = [int]$responseObj.StatusCode } catch {}
            }
            if ($null -ne $webError.ErrorDetails -and -not [string]::IsNullOrEmpty([string]$webError.ErrorDetails.Message)) {
                $responseText = [string]$webError.ErrorDetails.Message
            }
            if ([string]::IsNullOrEmpty($responseText) -and $null -ne $responseObj) {
                try {
                    $stream = $responseObj.GetResponseStream()
                    if ($null -ne $stream) {
                        $reader = New-Object System.IO.StreamReader($stream)
                        try { $responseText = $reader.ReadToEnd() }
                        finally { $reader.Dispose() }
                    }
                } catch {}
            }
        }
        $code = '-'
        $trace = '-'
        $groq = '-'
        try {
            $parsed = $responseText | ConvertFrom-Json -ErrorAction Stop
            if ($null -ne $parsed.PSObject.Properties['code']) { $code = [string]$parsed.code }
            if ($null -ne $parsed.PSObject.Properties['trace_id']) { $trace = [string]$parsed.trace_id }
            if ($null -ne $parsed.PSObject.Properties['groq_called']) { $groq = [string]$parsed.groq_called }
        } catch {}
        Write-Host ("Checagem {0}/12 | HTTP {1} | code={2} | groq_called={3} | trace_id={4}" -f $i, $status, $code, $groq, $trace)
        if ($groq -eq 'True') {
            Write-Host 'ABORTADO: resposta inconsistente (Groq indicado).'
            break
        }
        if ($status -eq 429 -and $code -eq 'diagnostic_rate_limited' -and $groq -eq 'False') {
            Write-Host 'SEC-053 APROVADO: binding negou checagem na chave isolada, sem Groq.'
            $approved = $true
            break
        }
        if ($status -ne 200 -or $code -ne 'diagnostic_allowed' -or $groq -ne 'False') {
            Write-Host 'INCONCLUSIVO: resposta inesperada; nao tentar novamente.'
            break
        }
        if ($watch.Elapsed.TotalSeconds -ge 45) {
            Write-Host 'INCONCLUSIVO: janela do ensaio encerrada.'
            break
        }
        if ($i -lt $maxRequests) { Start-Sleep -Milliseconds 900 }
    }
    $watch.Stop()
    if (-not $approved) { Write-Host 'SEC-053 inconclusivo: nao observamos bloqueio real neste ensaio.' }
    Write-Host ("Duracao total: {0:N1}s" -f $watch.Elapsed.TotalSeconds)
}
finally {
    if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    $plainCode = $null
    $secret = $null
    $ProgressPreference = $previousProgress
}
