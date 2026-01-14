# Final Report – Educational Trojan Horse Simulation

## 1. Objective
This project implements a safe Trojan horse simulation for educational purposes. The system demonstrates deceptive behaviors using dummy data only, enforces strict sandbox execution, and provides transparent logging and a defense mode to illustrate antivirus detection and response.

## 2. Scope
In scope:
- Authentication with RBAC and 2FA
- Dummy-file simulation of Trojan-like actions inside a whitelisted sandbox directory
- Transparent activity logging
- Defense mode detection + quarantine + restore
- Mandatory ethical safeguards (kill switch, auto-disable, disclaimer, signed agreement)

Out of scope:
- Any real malware functionality
- Any operation outside designated sandbox
- Any distribution beyond educational use

## 3. System Architecture
Components:
- FastAPI API server
- SQLite database for users and logs
- Sandbox folder (SANDBOX_ROOT) for all dummy data operations

Data flow:
1) User authenticates with password
2) User verifies OTP (TOTP)
3) API issues JWT
4) Simulation endpoints validate:
   - JWT + role
   - sandbox whitelisting
   - kill switch and time-based auto-disable
5) Actions occur only on dummy files and are logged
6) Defense mode scans for suspicious artifacts and quarantines/restores files

## 4. Core Features Mapping (Project Requirements)
### 4.1 Secure Login with RBAC + 2FA
- Roles: ADMIN and USER
- 2FA: TOTP using PyOTP
- JWT used for session authentication

### 4.2 Simulated Malicious Behaviors (Dummy Data Only)
1) Scan and remove viruses
- Deletes only `*.dummy_virus.txt` in sandbox dummy folder.

2) Speed up computer
- Creates file copies of notes to simulate performance slowdown (hard capped).

3) Fix system problems
- Renames and hides dummy report file by moving it into a hidden folder.

### 4.3 Transparent Activity Log
- Logs all actions (timestamp, user, role, action, status, reason, details).
- Admin can view logs via `/logs`.

### 4.4 Defense Mode (Antivirus demonstration)
- Detection heuristics:
  - signature matches for dummy virus names
  - detection of mass copy artifacts
  - detection of hidden dotfiles
- Response actions:
  - quarantine suspicious files into sandbox quarantine folder
  - restore functionality to revert changes

### 4.5 Sandbox Enforcer
- All file operations are blocked outside SANDBOX_ROOT using realpath checks.
- This ensures the simulation cannot execute on non-sandboxed systems.

## 5. Ethical Requirements (Mandatory)
- Kill switch: `.kill` file disables simulation
- Auto-disable: `.created_at` disables after 24 hours
- Directory whitelisting: sandbox-only operations
- Disclaimer displayed: "Educational simulation - all actions reversible"
- Ethical Use Agreement: signed by all team members
- Non-distribution statement included in documentation

## 6. Minimum Technical Requirements

### 6.1 Authentication & Authorization
- Secure login + hashed password storage (bcrypt via passlib)
- RBAC roles enforced on endpoints
- OTP-based 2FA (TOTP)

### 6.2 Security Testing (3 tools integrated)
- Bandit (SAST)
- Semgrep (SAST)
- OWASP ZAP Baseline (DAST)
Findings and remediation summary included in `docs/SECURITY_TESTING.md`.

### 6.3 CI/CD Pipeline
GitHub Actions stages:
- Build (import check)
- Security Scan (Bandit + Semgrep + ZAP)
- Test (pytest)
- Deploy (Docker build)

### 6.4 Documentation
- README setup and usage
- Ethics and safety controls documentation
- Security testing documentation
- This final report

## 7. Testing Strategy
Automated tests include:
- RBAC enforcement (User blocked from Admin endpoints)
- OTP-based authentication success path
- Sandbox traversal blocked
- Kill switch blocks simulation endpoints
- Auto-disable after 24 hours blocks simulation endpoints

## 8. Limitations
- Defense mode is heuristic-based for educational purposes and does not represent a production antivirus.
- Dummy data operations are intentionally constrained to maintain safety.

## 9. Conclusion
The project meets all stated requirements: secure authentication with RBAC and 2FA, safe dummy-file simulation of Trojan behaviors, transparent logging, defense mode, strict sandbox enforcement, mandatory ethical safeguards, integrated security testing tools, and CI/CD automation.
