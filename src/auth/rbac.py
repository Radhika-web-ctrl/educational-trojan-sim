from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.security import decode_token
from src.config import get_settings
from src.db import db_conn

bearer = HTTPBearer(auto_error=True)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    settings = get_settings()
    token = creds.credentials
    payload = decode_token(token, settings.jwt_secret)

    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    with db_conn() as conn:
        row = conn.execute("SELECT username, role, is_active FROM users WHERE username=?", (username,)).fetchone()
    if not row or row["is_active"] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

    return {"username": row["username"], "role": row["role"]}


def require_role(required_role: str):
    def _guard(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role.")
        return user

    return _guard
