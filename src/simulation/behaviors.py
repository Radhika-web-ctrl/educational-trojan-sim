from __future__ import annotations

import os
import shutil
import glob
from typing import Any

from src.sandbox_guard import assert_in_sandbox, ensure_dir


def scan_and_remove_viruses(sandbox_root: str) -> dict[str, Any]:
    dummy_dir = os.path.join(sandbox_root, "dummy")
    assert_in_sandbox(sandbox_root, dummy_dir)

    targets = glob.glob(os.path.join(dummy_dir, "*.dummy_virus.txt"))
    deleted = []
    for t in targets:
        assert_in_sandbox(sandbox_root, t)
        os.remove(t)
        deleted.append(os.path.basename(t))

    return {"deleted_count": len(deleted), "deleted_files": deleted}


def speed_up_computer_simulation(sandbox_root: str, copies: int = 200) -> dict[str, Any]:
    dummy_dir = os.path.join(sandbox_root, "dummy")
    assert_in_sandbox(sandbox_root, dummy_dir)

    copies = max(1, min(int(copies), 300))  # hard safety cap
    src_file = os.path.join(dummy_dir, "notes.txt")
    if not os.path.exists(src_file):
        raise FileNotFoundError("notes.txt missing. Run /sandbox/init first.")

    created = []
    for i in range(1, copies + 1):
        dst = os.path.join(dummy_dir, f"notes_copy_{i:03d}.txt")
        assert_in_sandbox(sandbox_root, dst)
        shutil.copy2(src_file, dst)
        created.append(os.path.basename(dst))

    return {"copies_created": len(created), "sample": created[:5]}


def fix_system_problems_simulation(sandbox_root: str) -> dict[str, Any]:
    dummy_dir = os.path.join(sandbox_root, "dummy")
    assert_in_sandbox(sandbox_root, dummy_dir)

    src = os.path.join(dummy_dir, "system_report.txt")
    if not os.path.exists(src):
        raise FileNotFoundError("system_report.txt missing. Run /sandbox/init first.")

    hidden = os.path.join(dummy_dir, ".system_report.txt")
    assert_in_sandbox(sandbox_root, hidden)
    os.rename(src, hidden)

    # optional hidden folder
    hidden_folder = os.path.join(dummy_dir, ".system")
    ensure_dir(hidden_folder)
    assert_in_sandbox(sandbox_root, hidden_folder)

    moved = os.path.join(hidden_folder, ".system_report.txt")
    assert_in_sandbox(sandbox_root, moved)
    os.rename(hidden, moved)

    return {"renamed_and_hidden": True, "new_path": moved}
