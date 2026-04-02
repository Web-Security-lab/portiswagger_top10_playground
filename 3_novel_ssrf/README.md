# Training-Environment---Novel-SSRF

## 시나리오

AWS EC2 위에서 동작하는 내부 URL Fetcher 서비스가 발견되었습니다.  
운영팀은 메타데이터 서버 접근이 완벽히 차단되어 있다고 확신합니다.  
정말 그럴까요?

---

## 서비스 정보

| 항목 | 값 |
|---|---|
| Web App | http://localhost:8080 |
| 목표 | 서버의 IAM 자격증명 탈취 |

---

## 환경 실행

```bash
docker-compose up -d
```

---

## 목표

서버의 IAM 자격증명(`AccessKeyId`, `SecretAccessKey`, `Token`)을 탈취하세요.

---