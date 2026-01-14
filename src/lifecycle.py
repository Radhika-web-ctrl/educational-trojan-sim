from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from src.sandbox_guard import ensure_dir

CREATED_AT_FILE = ".created_at"
KILL_FILE = ".kill"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def init_lifecycle_files(sandbox_root: str) -> None:
    ensure_dir(sandbox_root)
    created_at_path = os.path.join(sandbox_root, CREATED_AT_FILE)
    if not os.path.exists(created_at_path):
        with open(created_at_path, "w", encoding="utf-8") as f:
            f.write(utcnow().isoformat())


def is_simulation_enabled(sandbox_root: str, auto_disable_hours: int) -> tuple[bool, str]:
    kill_path = os.path.join(sandbox_root, KILL_FILE)
    if os.path.exists(kill_path):
        return False, "Kill switch active (.kill present)."

    created_at_path = os.path.join(sandbox_root, CREATED_AT_FILE)
    if not os.path.exists(created_at_path):
        return False, "Lifecycle not initialized (.created_at missing)."

    with open(created_at_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    try:
        created = datetime.fromisoformat(raw)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
    except Exception:
        return False, "Invalid .created_at timestamp."

    if utcnow() > created + timedelta(hours=auto_disable_hours):
        return False, f"Auto-disabled after {auto_disable_hours} hours."
    return True, "Enabled."
