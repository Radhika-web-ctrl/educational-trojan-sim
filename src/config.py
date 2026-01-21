from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str
    jwt_secret: str
    jwt_expires_min: int
    sandbox_root: str
    auto_disable_hours: int
    admin_bootstrap_username: str
    admin_bootstrap_password: str


def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me"),
        jwt_expires_min=int(os.getenv("JWT_EXPIRES_MIN", "60")),
        sandbox_root=os.getenv("SANDBOX_ROOT", "./sandbox_test"),
        auto_disable_hours=int(os.getenv("AUTO_DISABLE_HOURS", "24")),
        admin_bootstrap_username=os.getenv("ADMIN_BOOTSTRAP_USERNAME", "admin"),
        admin_bootstrap_password=os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "Admin@12345"),
    )
