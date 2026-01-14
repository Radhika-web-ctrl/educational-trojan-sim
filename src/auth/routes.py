from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends

from src.config import get_settings
from src.db import db_conn
from src.models import LoginRequest, LoginResponse, VerifyOtpRequest, TokenResponse
from src.auth.security import verify_password, verify_totp, create_access_token, create_totp_secret, hash_password
from src.auth.rbac import require_role
from src.logging_store import log_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    with db_conn() as conn:
        row = conn.execute("SELECT username, password_hash, role, totp_secret FROM users WHERE username=?",
                           (payload.username,)).fetchone()
    if not row or not verify_password(payload.password, row["password_hash"]):
        log_event(payload.username, "unknown", "auth_login", "blocked", "Invalid credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    log_event(row["username"], row["role"], "auth_login", "success", details={"otp_required": True})
    return LoginResponse(message="Password verified. Please submit OTP to /auth/verify-otp.")


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOtpRequest):
    settings = get_settings()
    with db_conn() as conn:
        row = conn.execute("SELECT username, role, totp_secret FROM users WHERE username=?",
                           (payload.username,)).fetchone()
    if not row:
        log_event(payload.username, "unknown", "auth_verify_otp", "blocked", "Unknown user")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user.")

    if not verify_totp(row["totp_secret"], payload.otp):
        log_event(row["username"], row["role"], "auth_verify_otp", "blocked", "Invalid OTP")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP.")

    token = create_access_token(row["username"], row["role"], settings.jwt_secret, settings.jwt_expires_min)
    log_event(row["username"], row["role"], "auth_verify_otp", "success")
    return TokenResponse(access_token=token)


@router.post("/admin/create-user")
def admin_create_user(
    username: str,
    password: str,
    role: str = "USER",
    admin: dict = Depends(require_role("ADMIN")),
):
    if role not in {"ADMIN", "USER"}:
        raise HTTPException(status_code=400, detail="role must be ADMIN or USER")

    secret = create_totp_secret()
    with db_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, totp_secret) VALUES (?, ?, ?, ?)",
                (username, hash_password(password), role, secret),
            )
            conn.commit()
        except Exception:
            raise HTTPException(status_code=400, detail="User already exists or invalid input.")

    log_event(admin["username"], admin["role"], "admin_create_user", "success", details={"new_user": username, "role": role})
    return {"status": "ok", "username": username, "role": role, "totp_secret": secret}
