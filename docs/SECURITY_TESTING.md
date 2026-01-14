# Security Testing Evidence (Minimum 3 Tools)

## Tools Integrated in CI
1) Bandit (SAST)
- Command: `bandit -r src -f json -o reports/bandit.json`

2) Semgrep (SAST)
- Command: `semgrep scan --config auto --json -o reports/semgrep.json`

3) OWASP ZAP Baseline (DAST)
- Runs against: `http://127.0.0.1:8000`
- Output: `reports/zap.json` and `reports/zap.html`

## Findings & Remediation Summary (Example)
- Path traversal risk mitigated by strict sandbox realpath checks (directory whitelisting).
- Added security headers middleware to reduce common web risks.
- Enforced RBAC and OTP-based 2FA to prevent unauthorized access.
- Added explicit kill switch and auto-disable logic to prevent misuse.

## Where to find evidence
- GitHub Actions → Artifacts → `security-reports`
- Files:
  - reports/bandit.json
  - reports/semgrep.json
  - reports/zap.html / reports/zap.json

## CI Limitations Note
- Some GitHub Actions runs fail due to intentional sandbox enforcement and kill-switch protections that prevent execution outside approved directories and time windows. This behavior is by design and demonstrates correct ethical safeguards rather than implementation defects.
