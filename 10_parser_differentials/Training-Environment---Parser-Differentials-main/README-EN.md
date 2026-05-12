# Training Environment - Parser Differentials

This is a wargame-style training environment inspired by **Parser Differentials: When Interpretation Becomes a Vulnerability**, ranked 10th in PortSwigger's Top 10 Web Hacking Techniques 2025.

The challenge demonstrates how an API Gateway and a legacy backend can interpret the same HTTP request differently.

## Challenge

A company protects its internal report service with an API Gateway.

The gateway believes it only forwards requests that satisfy both conditions:

- The path starts with `/api/public/`
- The JSON body has `scope=public`

However, the backend uses a legacy parser.

- The gateway checks access control against the raw URL path.
- The backend repeatedly URL-decodes and normalizes the path.
- The gateway JSON parser keeps the **first** duplicate key value.
- The backend JSON parser keeps the **last** duplicate key value.

Exploit both interpretation gaps to read the internal report and obtain the flag.

## Run

```bash
docker compose up --build
```

The service runs at `http://localhost:18010`.

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

Read the internal report:

```text
/api/internal/report
```

Direct access is blocked by the gateway.

## Intended Vulnerability

The intended exploit chains two parser differentials.

### 1. Path interpretation differential

The gateway checks whether the raw path starts with `/api/public/`.

The backend repeatedly URL-decodes the path and then normalizes path segments.

This can make the gateway-approved path route to a different backend path.

### 2. JSON duplicate key interpretation differential

The gateway keeps the first duplicate key value.

The backend uses Python's default `json.loads()` behavior and keeps the last duplicate key value.

The gateway may see `scope=public`, while the backend sees `scope=internal`.

## Difficulty

- Category: Web
- Topic: Parser Differential, URL Normalization, Duplicate JSON Key

## Spoiler

See `docs/solution.md` or `solver/solve.py` for the intended exploit.
