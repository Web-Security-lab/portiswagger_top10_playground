# Error-Based SSTI Lab

Top 10 web hacking techniques of 2025 에 소개되었던 **Successful Errors: New Code Injection and SSTI Techniques**의 주제에 대하여 실습해볼 수 있는 Lab 입니다.

## Summary

사용자가 Jinja2 템플릿 코드를 입력하면 서버에서 렌더링하는 웹 애플리케이션입니다.  
그러나 렌더링 결과는 절대 노출되지 않고, 성공 시 고정 메시지만 반환됩니다. 유일한 데이터 유출 경로는 에러 메시지입니다.

| Item | Detail |
|------|--------|
| Category | Web Exploitation |
| Technique | Error-Based SSTI |
| Framework | Flask 3.0 / Jinja2 |
| Difficulty | Easy |
| Filtering | None |

## Environment

```
/
├── app/                       # 챌린지 소스코드
│   ├── app.py                 # Flask 앱 (SSTI 취약점 포함)
│   ├── templates/
│   │   └── index.html         # 단일 Output UI
│   └── static/
│       └── style.css
├── docs/                      # 문서
│   ├── README.md              # 이 파일
│   └── SOLVE.md               # 풀이 writeup
├── Dockerfile                 # Python 3.11-slim, gunicorn
├── docker-compose.yml         # Port 52411, 보안 설정
├── requirements.txt           # flask==3.0.0, gunicorn==21.2.0
└── .gitignore
```

| Component | Detail |
|-----------|--------|
| Base Image | `python:3.11-slim` |
| WSGI Server | Gunicorn (2 workers, gthread) |
| Port | `52411` → container `5000` |
| Security | non-root user, read-only fs, `cap_drop: ALL`, `no-new-privileges`, resource limits |

## How to Run

```bash
# 1. Clone
git clone https://github.com/fox5t4r/Error-Based-SSTI-Lab.git
cd Error-Based-SSTI-Lab

# 2. Build & Run
docker compose up --build

# 3. Access
# http://localhost:52411
```

커스텀 플래그를 사용하려면:

```bash
FLAG="FLAG{my_custom_flag}" docker compose up --build
```

## Demo

<!-- 시연 영상/스크린샷을 여기에 추가하세요 -->
<!-- 예: ![demo](assets/demo.gif) -->

## License

For educational purposes only.
