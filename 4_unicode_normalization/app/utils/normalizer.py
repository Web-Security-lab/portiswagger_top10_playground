import unicodedata
import re


def safe_normalize(text: str) -> str:
    text = unicodedata.normalize('NFC', text)
    text = unicodedata.normalize('NFKC', text)
    return text

def normalize_for_storage(text: str) -> str:
    return unicodedata.normalize('NFC', text)

def normalize_email(email: str) -> str:
    if '@' not in email:
        return safe_normalize(email)

    local, _, domain = email.partition('@')
    local  = safe_normalize(local)
    domain = domain.lower()

    return f"{local}@{domain}"

def get_normalization_info(text: str) -> dict:
    return {
        'original': text,
        'NFC':      unicodedata.normalize('NFC',  text),
        'NFD':      unicodedata.normalize('NFD',  text),
        'NFKC':     unicodedata.normalize('NFKC', text),
        'NFKD':     unicodedata.normalize('NFKD', text),
        'codepoints': [
            {'char': c, 'hex': f'U+{ord(c):04X}', 'name': unicodedata.name(c, '?')}
            for c in text
        ],
    }