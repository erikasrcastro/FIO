# SEC-052 | FIO: verificacao controlada do rate limiter (PowerShell 5.1 ou 7).
# Maximo 6 chamadas; sem retry automatico; sem imprimir, salvar ou enviar segredos para terceiros.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$uri = 'https://fio.erika-srcastro.workers.dev/api/chat'
$maxRequests = 6
$secret = Read-Host 'Cole FIO_DEMO_ACCESS_KEY (NAO a chave GROQ_API_KEY)' -AsSecureString
$ptr = [IntPtr]::Zero
$plainCode = $null
$previousProgress = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
try {
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $plainCode = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    if ([string]::IsNullOrWhiteSpace($plainCode) -or $plainCode.Length -lt 24) {
        Write-Host 'Codigo invalido. Nenhum pedido enviado.'
        return
    }
    $payload = @{
        mode       = 'full'
        provider   = 'groq'
        task       = 'Revisar relatorio ficticio'
        stop_point = 'Secao final'
        next_step  = 'Revisar o ultimo paragrafo'
        message    = 'Fiz uma pausa e quero retomar a revisao.'
    } | ConvertTo-Json -Compress
    Write-Host 'SEC-052 | no maximo 6 solicitacoes, usando apenas os planos Free.'
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
        try {
            $parsed = $responseText | ConvertFrom-Json -ErrorAction Stop
            if ($null -ne $parsed.PSObject.Properties['code']) { $code = [string]$parsed.code }
            if ($null -ne $parsed.PSObject.Properties['trace_id']) { $trace = [string]$parsed.trace_id }
        } catch {}
        Write-Host ("Tentativa {0}/6 | HTTP {1} | code={2} | trace_id={3}" -f $i,$status,$code,$trace)
        if ($status -eq 429 -and $code -eq 'groq_rate_limited') {
            Write-Host 'SEC-052 APROVADO: bloqueio identificado no limitador Cloudflare.'
            $approved = $true
            break
        }
        if ($status -eq 429 -and $code -eq 'groq_free_quota_exceeded') {
            Write-Host 'INCONCLUSIVO: limite da Groq Free; nao comprova limitador Cloudflare.'
            break
        }
        if ($status -eq 429) {
            Write-Host 'INCONCLUSIVO: 429 sem codigo identificando a origem.'
            break
        }
        if ($status -eq 403) {
            Write-Host 'INTERROMPIDO: FIO_DEMO_ACCESS_KEY nao autorizada.'
            break
        }
        if ($status -ne 200) {
            Write-Host 'INTERROMPIDO: status inesperado. Nenhum novo pedido.'
            break
        }
        if ($watch.Elapsed.TotalSeconds -ge 50) {
            Write-Host 'INCONCLUSIVO: fim da janela de tempo do ensaio.'
            break
        }
        if ($i -lt $maxRequests) { Start-Sleep -Milliseconds 500 }
    }
    $watch.Stop()
    if (-not $approved) { Write-Host 'SEC-052 permanece pendente.' }
    Write-Host ("Duracao total: {0:N1}s" -f $watch.Elapsed.TotalSeconds)
}
finally {
    if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    $plainCode = $null
    $secret = $null
    $ProgressPreference = $previousProgress
}
