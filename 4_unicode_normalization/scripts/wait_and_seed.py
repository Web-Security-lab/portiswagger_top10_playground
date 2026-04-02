import os
import sys
import time

sys.path.insert(0, '/app')

import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash

_DB_CONF = {
    'host':        os.environ.get('DB_HOST',     'db'),
    'port':        int(os.environ.get('DB_PORT', '3306')),
    'user':        os.environ.get('DB_USER',     'polylot'),
    'password':    os.environ.get('DB_PASSWORD', 'p0ly10t_db_s3cr3t_2025'),
    'database':    os.environ.get('DB_NAME',     'polylot_db'),
    'charset':     'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit':  False,
}

def wait_for_db(max_attempts: int = 30, delay: float = 2.0) -> pymysql.Connection:
    for attempt in range(1, max_attempts + 1):
        try:
            conn = pymysql.connect(**_DB_CONF)
            print(f"[seed] DB connected (attempt {attempt})", flush=True)
            return conn
        except pymysql.err.OperationalError as e:
            print(f"[seed] DB not ready ({e}). Retrying in {delay}s...", flush=True)
            time.sleep(delay)

    print("[seed] ERROR: Could not connect to DB after max attempts.", flush=True)
    sys.exit(1)

_DEMO_USERS = [
    ('alice@example.com',  'Alice Chen',      'polylot123'),
    ('bob@example.com',    'Бобр Бобров',     'polylot123'),
    ('carol@example.com',  'キャロル 田中',   'polylot123'),
]

_DEMO_NOTES = [
    (
        0,  # alice
        'Hello World in Many Languages',
        (
            'English:    Hello, World!\n'
            'Korean:     안녕하세요, 세상!\n'
            'Japanese:   こんにちは、世界！\n'
            'Arabic:     مرحبا بالعالم\n'
            'Russian:    Привет, мир!\n'
            'Chinese:    你好，世界！\n'
            'Greek:      Γεια σου, Κόσμε!\n'
            'Thai:       สวัสดี โลก\n'
            'Hindi:      नमस्ते दुनिया\n'
            'Hebrew:     שלום עולם'
        ),
        'mul', 1,
    ),
    (
        0,  # alice
        'Unicode Normalization Forms Explained',
        (
            'Unicode defines four normalization forms:\n\n'
            'NFC  — Canonical Decomposition followed by Canonical Composition.\n'
            '        Most common form. Used by most operating systems and databases.\n'
            '        Example: é stored as a single code point U+00E9.\n\n'
            'NFD  — Canonical Decomposition only.\n'
            '        Splits precomposed characters into base + combining marks.\n'
            '        Example: é split into U+0065 (e) + U+0301 (combining acute).\n\n'
            'NFKC — Compatibility Decomposition followed by Canonical Composition.\n'
            '        Converts compatibility characters to their canonical equivalents.\n'
            '        Example: ① → 1,  ℌ → H,  ﬁ → fi,  ² → 2,  Ａ → A.\n\n'
            'NFKD — Compatibility Decomposition only.\n'
            '        Fully decomposes compatibility characters.\n\n'
            'Key insight: NFKC is lossy — it changes the visual appearance\n'
            'of certain characters. This can have security implications when\n'
            'normalization is applied at different stages of processing.'
        ),
        'en', 1,
    ),
    (
        1,  # bob (Cyrillic)
        'Заметки о кириллице',
        (
            'Кириллический алфавит используется для записи более 50 языков.\n\n'
            'Русский алфавит содержит 33 буквы:\n'
            'А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я\n\n'
            'Интересный факт: буква «Ё» часто заменяется на «Е» в неформальном письме,\n'
            'что иногда приводит к путанице в именах собственных.\n\n'
            'Unicode кириллица: U+0400 – U+04FF (основной блок).'
        ),
        'ru', 1,
    ),
    (
        2,  # carol (Japanese)
        'Japanese Writing Systems',
        (
            'Japanese uses three writing systems simultaneously:\n\n'
            'Hiragana (ひらがな) — 46 phonetic characters for native Japanese words.\n'
            '  a=あ, i=い, u=う, e=え, o=お\n\n'
            'Katakana (カタカナ) — 46 phonetic characters primarily for foreign words.\n'
            '  a=ア, i=イ, u=ウ, e=エ, o=オ\n\n'
            'Kanji (漢字) — Chinese-derived logographic characters.\n'
            '  日 (day/sun), 月 (month/moon), 山 (mountain), 川 (river)\n\n'
            'Common greetings:\n'
            '  こんにちは — Konnichiwa (Hello)\n'
            '  ありがとうございます — Arigatou gozaimasu (Thank you very much)\n'
            '  さようなら — Sayounara (Goodbye)'
        ),
        'ja', 1,
    ),
    (
        0,  # alice
        'CJK Compatibility Characters and NFKC',
        (
            'Unicode includes many "compatibility" characters for historical reasons.\n'
            'These look similar to ASCII but have different code points.\n'
            'Under NFKC normalization, they map to their ASCII equivalents:\n\n'
            'Fullwidth Latin:  Ａ Ｂ Ｃ → A B C\n'
            'Fullwidth Digits: ０ １ ２ → 0 1 2\n'
            'Circled Letters:  Ⓐ Ⓑ Ⓒ → A B C\n'
            'Circled Numbers:  ① ② ③ → 1 2 3\n'
            'Superscripts:     ¹ ² ³ → 1 2 3\n'
            'Fractions:        ½ ¼ ¾ → 1/2 1/4 3/4\n'
            'Ligatures:        ﬁ ﬂ → fi fl\n'
            'Half-width Kana:  ｱ ｲ ｳ → ア イ ウ\n\n'
            'Security note: If an application validates input before applying\n'
            'NFKC normalization, an attacker may use compatibility characters\n'
            'to bypass pattern-matching filters.'
        ),
        'en', 1,
    ),
    (
        1,  # bob
        'Greek Alphabet Reference',
        (
            'The Greek alphabet has 24 letters:\n\n'
            'Uppercase: Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω\n'
            'Lowercase: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω\n\n'
            'Many Greek letters look visually similar to Latin letters:\n'
            '  Α (U+0391 Greek Capital Letter Alpha) ≠ A (U+0041 Latin Capital Letter A)\n'
            '  Ο (U+039F Greek Capital Letter Omicron) ≠ O (U+004F Latin Capital Letter O)\n'
            '  ρ (U+03C1 Greek Small Letter Rho) ≠ p (U+0070 Latin Small Letter P)\n\n'
            'These "confusable" characters are catalogued at:\n'
            'https://util.unicode.org/UnicodeJsps/confusables.jsp'
        ),
        'el', 1,
    ),
]

def main() -> None:
    conn = wait_for_db()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM users")
            if cur.fetchone()['cnt'] > 0:
                print("[seed] Database already seeded. Skipping.", flush=True)
                return

        print("[seed] Seeding demo users and notes...", flush=True)

        user_ids: list[int] = []

        with conn.cursor() as cur:
            for email, display_name, password in _DEMO_USERS:
                cur.execute(
                    "INSERT INTO users (email, display_name, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (email, display_name, generate_password_hash(password))
                )
                user_ids.append(conn.insert_id())

            for user_idx, title, content, language, is_public in _DEMO_NOTES:
                cur.execute(
                    "INSERT INTO notes (user_id, title, content, language, is_public) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_ids[user_idx], title, content, language, is_public)
                )

        conn.commit()
        print(f"[seed] Seeded {len(_DEMO_USERS)} users and {len(_DEMO_NOTES)} notes.", flush=True)

    except Exception as e:
        conn.rollback()
        print(f"[seed] ERROR during seeding: {e}", flush=True)
        sys.exit(1)

    finally:
        conn.close()

if __name__ == '__main__':
    main()