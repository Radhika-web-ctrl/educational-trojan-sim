from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd.verify(password, password_hash)


def create_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str, otp: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(otp, valid_window=1)


def create_access_token(subject: str, role: str, jwt_secret: str, expires_min: int) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_min)).timestamp()),
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def decode_token(token: str, jwt_secret: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except JWTError as e:
        raise ValueError("Invalid token") from e
