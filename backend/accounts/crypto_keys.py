"""使用 SECRET_KEY 派生流与明文异或后再 Base64 编码存储（仅依赖标准库，避免环境缺少 Cryptodome/cryptography）。"""

import base64
import hashlib

from django.conf import settings

_SALT = b"fd-user-llm-api-key-v1"


def _xor_key_stream(length: int) -> bytes:
    seed = hashlib.sha256(settings.SECRET_KEY.encode("utf-8") + _SALT).digest()
    out = bytearray()
    i = 0
    while len(out) < length:
        chunk = hashlib.sha256(seed + i.to_bytes(4, "big")).digest()
        out.extend(chunk)
        i += 1
    return bytes(out[:length])


def encrypt_secret(plain: str) -> str:
    if not plain:
        return ""
    raw = plain.encode("utf-8")
    ks = _xor_key_stream(len(raw))
    enc = bytes(a ^ b for a, b in zip(raw, ks))
    return base64.urlsafe_b64encode(enc).decode("ascii")


def decrypt_secret(stored: str) -> str:
    if not stored:
        return ""
    try:
        enc = base64.urlsafe_b64decode(stored.encode("ascii"))
        ks = _xor_key_stream(len(enc))
        raw = bytes(a ^ b for a, b in zip(enc, ks))
        return raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return ""
