from __future__ import annotations

import os
import shutil
import json

from fastapi import APIRouter, Depends

from src.config import get_settings
from src.models import DefenseFindings, ActionResponse
from src.auth.rbac import require_role
from src.logging_store import log_event
from src.defense.detector import scan_findings
from src.sandbox_guard import ensure_dir, assert_in_sandbox

DISCLAIMER = "Educational simulation - all actions reversible"

router = APIRouter(prefix="/defense", tags=["defense"])


def _state_file(sandbox_root: str) -> str:
    return os.path.join(sandbox_root, "state.json")


def _load_state(sandbox_root: str) -> dict:
    p = _state_file(sandbox_root)
    if not os.path.exists(p):
        return {"moves": []}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(sandbox_root: str, state: dict) -> None:
    p = _state_file(sandbox_root)
    assert_in_sandbox(sandbox_root, p)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


@router.get("/scan", response_model=DefenseFindings)
def defense_scan(admin: dict = Depends(require_role("ADMIN"))):
    settings = get_settings()
    findings = scan_findings(settings.sandbox_root)
    log_event(admin["username"], admin["role"], "defense_scan", "success", details={"findings": findings})
    return DefenseFindings(findings=findings)


@router.post("/quarantine", response_model=ActionResponse)
def quarantine(admin: dict = Depends(require_role("ADMIN"))):
    settings = get_settings()
    dummy_dir = os.path.join(settings.sandbox_root, "dummy")
    quarantine_dir = os.path.join(settings.sandbox_root, "quarantine")

    ensure_dir(quarantine_dir)
    assert_in_sandbox(settings.sandbox_root, dummy_dir)
    assert_in_sandbox(settings.sandbox_root, quarantine_dir)

    findings = scan_findings(settings.sandbox_root)

    # Quarantine policy (simple + safe)
    to_move: list[str] = []
    for f in findings:
        if f["type"] == "signature_match":
            for item in f.get("items", []):
                to_move.append(os.path.join(dummy_dir, item))
        if f["type"] == "mass_copy_activity":
            # cap moves to avoid huge churn
            for name in sorted(os.listdir(dummy_dir)):
                if name.startswith("notes_copy_"):
                    to_move.append(os.path.join(dummy_dir, name))
            to_move = to_move[:50]

    moved = []
    state = _load_state(settings.sandbox_root)

    for src in to_move:
        if os.path.exists(src):
            assert_in_sandbox(settings.sandbox_root, src)
            dst = os.path.join(quarantine_dir, os.path.basename(src))
            assert_in_sandbox(settings.sandbox_root, dst)
            shutil.move(src, dst)
            moved.append({"from": src, "to": dst})
            state["moves"].append({"from": src, "to": dst})

    _save_state(settings.sandbox_root, state)

    log_event(admin["username"], admin["role"], "defense_quarantine", "success", details={"moved": moved})
    return ActionResponse(
        disclaimer=DISCLAIMER,
        status="ok",
        details={"moved_count": len(moved), "moved": moved},
    )


@router.post("/restore", response_model=ActionResponse)
def restore(admin: dict = Depends(require_role("ADMIN"))):
    settings = get_settings()
    state = _load_state(settings.sandbox_root)

    restored = []
    for m in reversed(state.get("moves", [])):
        src = m["to"]
        dst = m["from"]
        if os.path.exists(src):
            assert_in_sandbox(settings.sandbox_root, src)
            assert_in_sandbox(settings.sandbox_root, dst)
            ensure_dir(os.path.dirname(dst))
            shutil.move(src, dst)
            restored.append({"from": src, "to": dst})

    state["moves"] = []
    _save_state(settings.sandbox_root, state)

    log_event(admin["username"], admin["role"], "defense_restore", "success", details={"restored": restored})
    return ActionResponse(
        disclaimer=DISCLAIMER,
        status="ok",
        details={"restored_count": len(restored), "restored": restored},
    )
