"""使用 AES-CBC 加密存储用户 API Key（密钥由 Django SECRET_KEY 派生 SHA-256）。"""

import base64
import hashlib

from django.conf import settings

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Random import get_random_bytes
    from Cryptodome.Util.Padding import pad, unpad
except ImportError:  # pragma: no cover
    AES = None  # type: ignore


def _aes_key() -> bytes:
    return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def encrypt_secret(plain: str) -> str:
    if not plain:
        return ""
    if AES is None:
        raise RuntimeError("请安装 pycryptodome：pip install pycryptodome")
    raw = plain.encode("utf-8")
    iv = get_random_bytes(16)
    cipher = AES.new(_aes_key(), AES.MODE_CBC, iv)
    enc = cipher.encrypt(pad(raw, AES.block_size))
    return base64.b64encode(iv + enc).decode("ascii")


def decrypt_secret(stored: str) -> str:
    if not stored:
        return ""
    if AES is None:
        return ""
    try:
        data = base64.b64decode(stored.encode("ascii"))
        iv, enc = data[:16], data[16:]
        cipher = AES.new(_aes_key(), AES.MODE_CBC, iv)
        raw = unpad(cipher.decrypt(enc), AES.block_size)
        return raw.decode("utf-8")
    except (ValueError, TypeError, IndexError):
        return ""
