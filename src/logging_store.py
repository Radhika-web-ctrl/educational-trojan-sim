from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.db import db_conn


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    username: str,
    role: str,
    action: str,
    status: str,
    reason: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    payload = json.dumps(details or {}, ensure_ascii=False)
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO activity_logs (ts_utc, username, role, action, status, reason, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (utc_iso(), username, role, action, status, reason, payload),
        )
        conn.commit()


def fetch_logs(limit: int = 200) -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT ts_utc, username, role, action, status, reason, details_json FROM activity_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "ts_utc": r["ts_utc"],
                "username": r["username"],
                "role": r["role"],
                "action": r["action"],
                "status": r["status"],
                "reason": r["reason"],
                "details": json.loads(r["details_json"] or "{}"),
            }
        )
    return out
