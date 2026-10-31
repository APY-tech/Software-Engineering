"""口令散列与会话令牌。

REQ-012 要求密码加密存储、校验时不还原明文。这里使用标准库的
PBKDF2-HMAC-SHA256：同一条口令每次加盐的结果都不同，校验时用
密文比对，数据库被读走也无法直接得到口令。
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 120_000
_SALT_BYTES = 16
_TOKEN_BYTES = 24


def hash_password(password: str) -> str:
    """生成口令的密文，格式为 ``算法$轮数$盐$散列``。"""
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt,
                                 _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验口令。格式不合法或散列不符都返回 False，不抛异常。"""
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != _ALGORITHM:
        return False
    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt,
                                 iterations)
    return hmac.compare_digest(digest.hex(), parts[3])


def new_token() -> str:
    """生成不可预测的会话令牌。"""
    return secrets.token_urlsafe(_TOKEN_BYTES)
