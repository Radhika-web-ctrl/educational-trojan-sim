from __future__ import annotations

from src.sandbox_guard import assert_in_sandbox, SandboxError


def test_sandbox_blocks_outside_path():
    sandbox = "./sandbox_test"
    try:
        assert_in_sandbox(sandbox, "../outside.txt")
        assert False, "Expected SandboxError"
    except SandboxError:
        assert True
