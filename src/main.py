from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.db import init_db, db_conn
from src.auth.security import hash_password, create_totp_secret
from src.auth.routes import router as auth_router
from src.simulation.routes import router as sim_router
from src.defense.routes import router as defense_router
from src.auth.rbac import require_role
from src.sandbox.dummy_data import init_dummy_data
from src.lifecycle import init_lifecycle_files
from src.logging_store import fetch_logs, log_event
from src.security_headers import add_security_headers

DISCLAIMER = "Educational simulation - all actions reversible"

app = FastAPI(title="Educational Trojan Horse Simulation", version="1.0.0")


@app.middleware("http")
async def security_headers_mw(request, call_next):
    resp = await call_next(request)
    return add_security_headers(resp)


@app.on_event("startup")
def startup():
    settings = get_settings()
    init_db()
    init_lifecycle_files(settings.sandbox_root)
    bootstrap_admin(settings.admin_bootstrap_username, settings.admin_bootstrap_password)


def bootstrap_admin(username: str, password: str) -> None:
    # create admin if not exists
    with db_conn() as conn:
        row = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if row:
            return
        secret = create_totp_secret()
        conn.execute(
            "INSERT INTO users (username, password_hash, role, totp_secret) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), "ADMIN", secret),
        )
        conn.commit()


@app.get("/")
def root():
    return {
        "disclaimer": DISCLAIMER,
        "message": "Educational simulation API. Use /docs for interactive API documentation.",
    }


@app.post("/sandbox/init")
def sandbox_init(admin: dict = Depends(require_role("ADMIN"))):
    settings = get_settings()
    details = init_dummy_data(settings.sandbox_root)
    log_event(admin["username"], admin["role"], "sandbox_init_dummy_data", "success", details=details)
    return {"status": "ok", "details": details, "disclaimer": DISCLAIMER}


@app.get("/logs")
def get_logs(admin: dict = Depends(require_role("ADMIN"))):
    logs = fetch_logs(limit=200)
    return {"status": "ok", "logs": logs, "disclaimer": DISCLAIMER}


app.include_router(auth_router)
app.include_router(sim_router)
app.include_router(defense_router)
