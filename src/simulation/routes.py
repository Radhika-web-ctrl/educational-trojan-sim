from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config import get_settings
from src.models import ActionResponse
from src.auth.rbac import get_current_user
from src.lifecycle import is_simulation_enabled
from src.logging_store import log_event
from src.simulation.behaviors import (
    scan_and_remove_viruses,
    speed_up_computer_simulation,
    fix_system_problems_simulation,
)

DISCLAIMER = "Educational simulation - all actions reversible"

router = APIRouter(prefix="/sim", tags=["simulation"])


@router.post("/scan-remove", response_model=ActionResponse)
def scan_remove(user: dict = Depends(get_current_user)):
    settings = get_settings()
    ok, reason = is_simulation_enabled(settings.sandbox_root, settings.auto_disable_hours)
    if not ok:
        log_event(user["username"], user["role"], "sim_scan_remove", "blocked", reason)
        raise HTTPException(status_code=403, detail=reason)

    details = scan_and_remove_viruses(settings.sandbox_root)
    log_event(user["username"], user["role"], "sim_scan_remove", "success", details=details)
    return ActionResponse(disclaimer=DISCLAIMER, status="ok", details=details)


@router.post("/speedup", response_model=ActionResponse)
def speedup(copies: int = 200, user: dict = Depends(get_current_user)):
    settings = get_settings()
    ok, reason = is_simulation_enabled(settings.sandbox_root, settings.auto_disable_hours)
    if not ok:
        log_event(user["username"], user["role"], "sim_speedup", "blocked", reason)
        raise HTTPException(status_code=403, detail=reason)

    details = speed_up_computer_simulation(settings.sandbox_root, copies=copies)
    log_event(user["username"], user["role"], "sim_speedup", "success", details=details)
    return ActionResponse(disclaimer=DISCLAIMER, status="ok", details=details)


@router.post("/fix-system", response_model=ActionResponse)
def fix_system(user: dict = Depends(get_current_user)):
    settings = get_settings()
    ok, reason = is_simulation_enabled(settings.sandbox_root, settings.auto_disable_hours)
    if not ok:
        log_event(user["username"], user["role"], "sim_fix_system", "blocked", reason)
        raise HTTPException(status_code=403, detail=reason)

    details = fix_system_problems_simulation(settings.sandbox_root)
    log_event(user["username"], user["role"], "sim_fix_system", "success", details=details)
    return ActionResponse(disclaimer=DISCLAIMER, status="ok", details=details)
