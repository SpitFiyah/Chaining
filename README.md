# CIT Student Portal — Security Assessment PoCs & Findings Tools

**Target:** https://student.citexams.in | https://des.citexams.in | https://erp.citexams.in  
**Date:** August 2026  
**Assessor:** Authorized Security Assessment Team (mirafnan619@gmail.com)  
**Authorization:** Cambridge Institute of Technology IT Department (helpdeskexams@cit.edu.in)

---

## Findings & Proof-of-Concept Suite (`C:\Users\user\exam_results\Findings\`)

The `Findings` folder imported into the project contains custom scripts and session dumps generated during active assessment:

| Script / Artifact | Description & Purpose | Finding Proven |
|---|---|---|
| `810.py` | Automated multi-threaded session harvester that dumps PII from exposed `/storage/framework/sessions/` into CSV format | 🔴 SES-01 (Session & PII Exposure) |
| `forge_final12.py` | Complete Python implementation of Laravel's Encrypter (`AES-256-CBC` + PHP serialization + HMAC SHA256) to forge valid `laravel_session` cookies offsite using exposed `APP_KEY` | 🔴 SES-02 (Cryptographic Cookie Forgery) |
| `find_id.py` | Brute-forces student IDs (1 to 5000) using forged session cookies | 🔴 SES-02 (Session Forgery & User Enumeration) |
| `students_sessions` / `student_sessions.txt` | Harvested CSV database containing 620+ parsed active student records (Names, Emails, Phone numbers, Student IDs, Branches, Last URLs) | 🔴 SES-01 (Verifiable PII Data Breach) |

---

## Execution Instructions for Technical Reviewers

### 1. Mass Session Harvester (`810.py`)
```bash
python Findings/810.py
```
*Output:* Fetches all session files listed in `https://student.citexams.in/storage/framework/sessions/`, extracts PII attributes using regex, and saves `students_sessions.csv`.

### 2. Cryptographic Cookie Forgery (`forge_final12.py`)
```bash
python Findings/forge_final12.py
```
*Output:* Uses `APP_KEY` (`kbqL/05YWl0TZEnb3oE4811UauhKhWps...`) to construct a PHP-serialized session object for a target `student_id`, encrypts it using `AES-256-CBC`, computes the HMAC signature, and generates a valid `laravel_session` cookie string.

---

## Standard PoC PowerShell Suite (`C:\Users\user\exam_results\`)

| Script | Purpose |
|---|---|
| `poc_01_env_exposure.ps1` | Proves direct GET access to `.env` configuration file |
| `poc_02_appkey_decrypt.ps1` | Decrypts live `XSRF-TOKEN` cookie via `APP_KEY` |
| `poc_03_session_exposure.ps1` | Retrieves and parses live session PII from disk |
| `poc_04_log_exposure.ps1` | Downloads 13+ days of daily Laravel debug logs |
| `poc_05_directory_listing.ps1` | Verifies global directory indexing across `/storage/`, `/vendor/`, `/app/` |
