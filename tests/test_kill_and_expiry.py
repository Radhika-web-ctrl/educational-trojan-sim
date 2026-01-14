from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

import pyotp
from fastapi.testclient import TestClient

from src.main import app
from src.db import db_conn
from src.auth.security import hash_password, create_totp_secret
from src.config import get_settings

client = TestClient(app)


def create_user(username: str, password: str, role: str):
    secret = create_totp_secret()
    with db_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO users (username, password_hash, role, totp_secret, is_active) VALUES (?, ?, ?, ?, 1)",
            (username, hash_password(password), role, secret),
        )
        conn.commit()
    return secret


def get_token(username: str, secret: str):
    client.post("/auth/login", json={"username": username, "password": "Pass@12345"})
    otp = pyotp.TOTP(secret).now()
    return client.post("/auth/verify-otp", json={"username": username, "otp": otp}).json()["access_token"]


def test_kill_switch_blocks_sim():
    settings = get_settings()
    os.makedirs(settings.sandbox_root, exist_ok=True)
    kill = os.path.join(settings.sandbox_root, ".kill")
    with open(kill, "w", encoding="utf-8") as f:
        f.write("disable")

    secret = create_user("u3", "Pass@12345", "USER")
    token = get_token("u3", secret)

    r = client.post("/sim/speedup", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

    os.remove(kill)


def test_expiry_blocks_sim():
    settings = get_settings()
    os.makedirs(settings.sandbox_root, exist_ok=True)
    created_at = os.path.join(settings.sandbox_root, ".created_at")

    old = datetime.now(timezone.utc) - timedelta(hours=settings.auto_disable_hours + 1)
    with open(created_at, "w", encoding="utf-8") as f:
        f.write(old.isoformat())

    secret = create_user("u4", "Pass@12345", "USER")
    token = get_token("u4", secret)

    r = client.post("/sim/scan-remove", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
