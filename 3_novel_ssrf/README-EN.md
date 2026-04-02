# Training-Environment---Novel-SSRF

## Scenario

An internal URL Fetcher service has been discovered running on an AWS EC2 instance.
The operations team is confident that access to the metadata server is completely blocked.
Is it really?

---

## Service Info

| Item | Value |
|---|---|
| Web App | http://localhost:8080 |
| Goal | Steal the server's IAM credentials |

---

## Setup

```bash
docker-compose up -d
```

---

## Objective

Steal the server's IAM credentials (`AccessKeyId`, `SecretAccessKey`, `Token`).

---
