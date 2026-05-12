# Training Environment - Parser Differentials

PortSwigger Top 10 Web Hacking Techniques 2025의 10위 주제인 **Parser Differentials: When Interpretation Becomes a Vulnerability**를 기반으로 만든 워게임형 훈련 환경입니다.

이 문제는 단순한 중복 파라미터 문제가 아니라, **API Gateway와 Legacy Backend가 같은 HTTP 요청을 서로 다르게 해석하는 상황**을 다룹니다.

## Challenge

회사 내부 리포트 서비스 앞에는 API Gateway가 있습니다.

Gateway는 외부 사용자가 다음 조건을 만족하는 요청만 backend로 전달한다고 믿습니다.

- `/api/public/**` 경로만 허용
- JSON body의 `scope` 값은 `public`만 허용

하지만 backend는 오래된 legacy parser를 사용합니다.

- Gateway는 raw URL path를 기준으로 접근 제어를 수행합니다.
- Backend는 URL decode를 반복한 뒤 path normalization을 수행합니다.
- Gateway JSON parser는 duplicate key 중 **첫 번째 값**을 사용합니다.
- Backend JSON parser는 duplicate key 중 **마지막 값**을 사용합니다.

두 해석 차이를 연결해 내부 리포트를 읽고 flag를 획득하세요.

## Run

```bash
docker compose up --build
```

서비스는 기본적으로 `http://localhost:18010`에서 실행됩니다.

## Basic Endpoints

```bash
curl http://localhost:18010/api/public/status
```

```bash
curl -X POST http://localhost:18010/api/public/report \
  -H 'Content-Type: application/json' \
  --data '{"scope":"public"}'
```

## Goal

다음 내부 리포트에 접근하세요.

```text
/api/internal/report
```

단, 외부에서 직접 접근하면 Gateway가 차단합니다.

## Intended Vulnerability

이 문제의 핵심은 다음 두 가지 parser differential을 함께 이용하는 것입니다.

### 1. Path interpretation differential

Gateway는 raw path만 보고 `/api/public/`으로 시작하는지 검사합니다.

Backend는 URL decoding을 반복한 뒤 `..` segment를 normalize합니다.

따라서 Gateway가 보는 path와 Backend가 라우팅하는 path가 달라질 수 있습니다.

### 2. JSON duplicate key interpretation differential

Gateway는 JSON object의 duplicate key 중 첫 번째 값을 사용합니다.

Backend는 일반적인 Python `json.loads()` 동작처럼 duplicate key 중 마지막 값을 사용합니다.

즉 Gateway는 `scope=public`이라고 판단하지만, Backend는 `scope=internal`이라고 판단할 수 있습니다.

## Difficulty

- Category: Web
- Topic: Parser Differential, URL Normalization, Duplicate JSON Key

## Files

```text
.
├── app/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docs/
│   ├── challenge.md
│   └── solution.md
├── internal/
│   └── architecture.md
├── solver/
│   └── solve.py
├── docker-compose.yml
├── README.md
└── README-EN.md
```

## Spoiler

풀이가 필요하면 `docs/solution.md` 또는 `solver/solve.py`를 확인하세요.
