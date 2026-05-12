# Challenge Description

## Title

Interpretation Gap

## Description

우리 회사는 내부 보안 리포트 API를 외부에 노출하지 않기 위해 API Gateway를 도입했습니다.

Gateway는 `/api/public/**` 경로만 backend로 전달하고, JSON 요청에서 `scope=public`만 허용합니다.

하지만 backend는 오래된 legacy parser를 사용합니다. 같은 HTTP 요청이라도 Gateway와 Backend가 완전히 같은 방식으로 해석한다고 확신할 수 있을까요?

내부 리포트를 읽고 flag를 획득하세요.

## Target

```text
http://localhost:8080
```

## Known Public Endpoints

```text
GET  /api/public/status
POST /api/public/report
```

## Goal

```text
POST /api/internal/report
```

## Notes for Players

- Direct access to `/api/internal/report` is blocked.
- The public report only accepts `scope=public`.
- Look for places where the gateway and backend may disagree.
- The vulnerability is not SQL injection, XSS, SSTI, or command injection.
