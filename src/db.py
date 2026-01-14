from __future__ import annotations

import sqlite3
from typing import Iterator
from contextlib import contextmanager

DB_PATH = "app.sqlite"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                totp_secret TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_utc TEXT NOT NULL,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                details_json TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sim_state (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            );
            """
        )
        conn.commit()


@contextmanager
def db_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()
