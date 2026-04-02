# Training-Environment---Blind-ORM-Leak

## 기본 요약

사내 사용자 검색 시스템이 새로 배포되었습니다.  
개발팀은 유연한 검색 기능을 추가했다고 자랑하지만, 관리자 메모는 외부에 노출되지 않는다고 믿고 있습니다.

이 환경은 검색 API에서 사용자 입력이 ORM 필터의 필드명과 연산자로 직접 반영될 때 발생할 수 있는 **Blind ORM Leak** 취약점을 학습하기 위한 훈련 환경입니다.  
공격자는 검색 결과의 개수 차이를 오라클로 활용하여 관리자 계정의 비밀 메모에 저장된 플래그를 추론할 수 있습니다.

---

## 환경 디렉토리

```text
Training-Environment---Blind-ORM-Leak/
├── app/                  # 외부 공개 취약 웹 애플리케이션
├── internal/             # 내부 전용 플래그 제공 서비스
├── docs/                 # 문제 해설 및 익스플로잇 문서
├── solver/               # intended solver 스크립트
├── docker-compose.yml    # 전체 환경 실행 파일
├── README.md
└── README-EN.md
```

---

## 서비스 정보

| 항목    | 값                                           |
| ------- | -------------------------------------------- |
| Web App | http://localhost:8080                        |
| 목표    | 관리자 계정의 비밀 메모에 저장된 플래그 획득 |

---

## 실행 방법

### 환경 실행

```bash
docker compose up -d --build
```

---

## 목표

서버의 `admin.secret_note`에 저장된 플래그 `WSL{...}` 를 획득하세요.
