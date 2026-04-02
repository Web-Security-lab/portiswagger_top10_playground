import re
from typing import Union


_SQLI_PATTERN = re.compile(
    r"(?:'|\"|--|/\*|\*/|;|\bOR\b|\bAND\b|"
    r"\bunion\b|\bselect\b|\binsert\b|\bupdate\b|"
    r"\bdelete\b|\bdrop\b|\bcreate\b|\balter\b|"
    r"\bexec\b|\bsleep\b|\bbenchmark\b)",
    re.IGNORECASE
)

def check_sqli(value: str) -> bool:
    return bool(_SQLI_PATTERN.search(value))

_XSS_PATTERN = re.compile(
    r'(<\s*script|javascript\s*:|on\w+\s*=|'
    r'<\s*iframe|<\s*svg|<\s*img\s+[^>]*onerror)',
    re.IGNORECASE
)

def check_xss(value: str) -> bool:
    return bool(_XSS_PATTERN.search(value))

def overlong_check(data: Union[bytes, bytearray]) -> bool:
    i = 0
    while i < len(data):
        b = data[i]

        if b < 0x80:
            i += 1
            continue

        if b < 0xC0:
            return True

        if b < 0xE0:
            if b < 0xC2:
                return True
            if i + 1 >= len(data) or (data[i + 1] & 0xC0) != 0x80:
                return True
            i += 2
            continue

        if b < 0xF0:
            if i + 2 >= len(data):
                return True
            b2 = data[i + 1]
            if b == 0xE0 and b2 < 0xA0:
                return True
            if (b2 & 0xC0) != 0x80 or (data[i + 2] & 0xC0) != 0x80:
                return True
            i += 3
            continue

        if b < 0xF8:
            if i + 3 >= len(data):
                return True
            b2 = data[i + 1]
            if b == 0xF0 and b2 < 0x90:
                return True
            if (b2 & 0xC0) != 0x80:
                return True
            if (data[i + 2] & 0xC0) != 0x80 or (data[i + 3] & 0xC0) != 0x80:
                return True
            i += 4
            continue

        return True

    return False
