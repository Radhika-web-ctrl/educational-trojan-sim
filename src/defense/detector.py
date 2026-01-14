from __future__ import annotations

import os
import glob
from typing import Any

from src.sandbox_guard import assert_in_sandbox


def scan_findings(sandbox_root: str) -> list[dict[str, Any]]:
    dummy_dir = os.path.join(sandbox_root, "dummy")
    assert_in_sandbox(sandbox_root, dummy_dir)

    findings: list[dict[str, Any]] = []

    # 1) Dummy virus signatures
    viruses = glob.glob(os.path.join(dummy_dir, "*.dummy_virus.txt"))
    if viruses:
        findings.append(
            {
                "type": "signature_match",
                "severity": "high",
                "items": [os.path.basename(v) for v in viruses],
            }
        )

    # 2) Mass copy activity
    copies = glob.glob(os.path.join(dummy_dir, "notes_copy_*.txt"))
    if len(copies) > 50:
        findings.append(
            {
                "type": "mass_copy_activity",
                "severity": "medium",
                "count": len(copies),
            }
        )

    # 3) Hidden artifacts (dotfiles/folders)
    hidden = glob.glob(os.path.join(dummy_dir, ".*"))
    hidden_names = [
        os.path.basename(h)
        for h in hidden
        if os.path.basename(h) not in [".", ".."]
    ]
    if hidden_names:
        findings.append(
            {
                "type": "hidden_artifacts",
                "severity": "medium",
                "items": hidden_names[:50],
            }
        )

    return findings
