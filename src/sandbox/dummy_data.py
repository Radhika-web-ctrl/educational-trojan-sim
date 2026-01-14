from __future__ import annotations

import os
from src.sandbox_guard import ensure_dir, assert_in_sandbox


def init_dummy_data(sandbox_root: str) -> dict:
    dummy_dir = os.path.join(sandbox_root, "dummy")
    quarantine_dir = os.path.join(sandbox_root, "quarantine")
    ensure_dir(dummy_dir)
    ensure_dir(quarantine_dir)

    # Ensure in sandbox
    assert_in_sandbox(sandbox_root, dummy_dir)
    assert_in_sandbox(sandbox_root, quarantine_dir)

    files = {
        "virus_01": os.path.join(dummy_dir, "virus_01.dummy_virus.txt"),
        "virus_02": os.path.join(dummy_dir, "virus_02.dummy_virus.txt"),
        "system_report": os.path.join(dummy_dir, "system_report.txt"),
        "notes": os.path.join(dummy_dir, "notes.txt"),
    }

    for k, p in files.items():
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Dummy file: {k}\nEducational simulation only.\n")

    return {"dummy_dir": dummy_dir, "quarantine_dir": quarantine_dir, "created": list(files.values())}
