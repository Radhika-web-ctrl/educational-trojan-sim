from __future__ import annotations

import pyotp
from fastapi.testclient import TestClient

from src.main import app
from src.config import get_settings
from src.db import db_conn
from src.auth.security import hash_password, create_totp_secret

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


def test_login_and_verify_otp():
    secret = create_user("u1", "Pass@12345", "USER")

    r = client.post("/auth/login", json={"username": "u1", "password": "Pass@12345"})
    assert r.status_code == 200

    otp = pyotp.TOTP(secret).now()
    r2 = client.post("/auth/verify-otp", json={"username": "u1", "otp": otp})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_rbac_admin_only_endpoint_denied_for_user():
    secret = create_user("u2", "Pass@12345", "USER")
    otp = pyotp.TOTP(secret).now()
    client.post("/auth/login", json={"username": "u2", "password": "Pass@12345"})
    token = client.post("/auth/verify-otp", json={"username": "u2", "otp": otp}).json()["access_token"]

    r = client.post("/sandbox/init", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
