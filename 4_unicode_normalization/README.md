# Scrambled (Polylot Notes)

다국어 메모 공유 서비스 **Polylot Notes**의 소스코드입니다.  
루트 경로에 존재하는 `flag`에 저장된 플래그 `WSL{...}`를 획득하세요.

## 서비스 구조

```
/
├── app/
│   ├── app.py              # Flask application factory
│   ├── config.py           # Application configuration
│   ├── db.py               # Database connection helper
│   ├── routes/
│   │   ├── main.py         # Homepage, dashboard, note view
│   │   ├── auth.py         # Register, login, logout, password reset
│   │   ├── api.py          # Notes CRUD API + public search
│   │   └── admin.py        # Admin translation preview API
│   ├── utils/
│   │   ├── normalizer.py   # Unicode normalization utilities
│   │   └── waf.py          # WAF helpers (SQLi, XSS, overlong detection)
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       └── note.html
├── db/
│   └── init.sql            # MySQL schema + seed data
├── scripts/
│   └── wait_and_seed.py    # DB init script (runs at container start)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── entrypoint.sh
```

## API Endpoints

### Public / Authenticated

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Homepage (recent public notes) |
| GET | `/notes/<id>` | View a single note |
| GET | `/auth/login` | Login page |
| POST | `/auth/login` | Login action |
| GET | `/auth/register` | Register page |
| POST | `/auth/register` | Register action |
| GET | `/auth/logout` | Logout |
| POST | `/auth/reset-password` | Password reset request |
| GET | `/dashboard` | User's note dashboard (auth required) |
| GET | `/api/notes/search?q=` | Search public notes (auth required) |
| POST | `/api/notes` | Create a note (auth required) |
| DELETE | `/api/notes/<id>` | Delete a note (auth required) |
| PATCH | `/api/notes/<id>` | Update a note (auth required) |
| GET | `/api/whoami` | Current user info (auth required) |

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/render?content=&lang=` | Translation preview renderer |
| GET | `/admin/status` | Admin API status |

Admin endpoints require the `X-Admin-Token` header.

## Database Schema

```sql
-- Users table (utf8mb4_0900_ai_ci collation)
users(id, email, display_name, password_hash, created_at)

-- Notes table
notes(id, user_id, title, content, language, is_public, created_at)

-- Admin sessions (static API token store)
admin_sessions(id, api_token)
```

## Notes

- 서비스는 다국어 콘텐츠 처리를 위해 여러 경로에서 Unicode 정규화를 수행합니다.
- 검색(`/api/notes/search`)은 국제 문자 지원을 위해 NFKC 정규화를 적용합니다.
- Admin 렌더 엔드포인트(`/admin/render`)는 번역 결과의 HTML 미리보기를 제공합니다.
- 비밀번호 재설정 기능(`/auth/reset-password`)은 현재 이메일 발송이 구현되지 않았습니다.

## How to Run

```bash
# 이미지 빌드 및 시작
docker compose up -d --build
```