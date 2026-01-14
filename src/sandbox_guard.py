from __future__ import annotations

import os


class SandboxError(Exception):
    pass


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def real(path: str) -> str:
    return os.path.realpath(os.path.abspath(path))


def assert_in_sandbox(sandbox_root: str, target_path: str) -> None:
    sr = real(sandbox_root)
    tp = real(target_path)
    if not tp.startswith(sr + os.sep) and tp != sr:
        raise SandboxError("Refusing to operate outside designated sandbox directory (whitelist enforced).")
