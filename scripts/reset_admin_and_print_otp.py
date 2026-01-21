from __future__ import annotations

import sys
from pathlib import Path

import pyotp
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Ensure project root is on PYTHONPATH (fixes: ModuleNotFoundError: 'src')
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------
# Load repo root .env reliably (Codespaces-safe, overrides stale env vars)
# ---------------------------------------------------------------------
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

from src.config import get_settings
from src.db import init_db, db_conn
from src.auth.security import hash_password, create_totp_secret


def main() -> None:
    settings = get_settings()
    init_db()

    username = settings.admin_bootstrap_username
    password = settings.admin_bootstrap_password

    # Generate a fresh TOTP secret so OTP is immediately usable
    secret = create_totp_secret()
    totp = pyotp.TOTP(secret)

    with db_conn() as conn:
        row = conn.execute(
            "SELECT username FROM users WHERE username=?",
            (username,),
        ).fetchone()

        if row:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?,
                    role = 'ADMIN',
                    totp_secret = ?,
                    is_active = 1
                WHERE username = ?
                """,
                (hash_password(password), secret, username),
            )
            print("[+] Existing admin updated.")
        else:
            conn.execute(
                """
                INSERT INTO users (username, password_hash, role, totp_secret, is_active)
                VALUES (?, ?, 'ADMIN', ?, 1)
                """,
                (username, hash_password(password), secret),
            )
            print("[+] Admin user created.")

        conn.commit()

    print("\n=== ADMIN RESET COMPLETE ===")
    print("Username       :", username)
    print("Password       :", password)
    print("TOTP secret    :", secret)
    print("Current OTP    :", totp.now())
    print("Provisioning URI:", totp.provisioning_uri(name=username, issuer_name="Educational-Trojan-Sim"))
    print("===========================\n")


if __name__ == "__main__":
    main()
