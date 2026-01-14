# Educational Trojan Horse Simulation (SAFE)

## Disclaimer (MANDATORY)
Educational simulation - all actions reversible

## Purpose
This project simulates deceptive Trojan-like behaviors in a controlled sandbox for educational use only. All actions operate on dummy data inside a whitelisted test directory and are designed to be reversible.

## Safety and Ethics (MANDATORY)
- Sandbox Enforcer (Directory Whitelisting): operations are refused outside the designated sandbox.
- Kill Switch: create `SANDBOX_ROOT/.kill` to disable simulation actions immediately.
- Auto-disable: simulation disables automatically after 24 hours from first initialization.
- Ethical Use Agreement: all team members must sign `docs/ETHICAL_USE_AGREEMENT.md`.
- Not for distribution outside educational context.

## Features
- Secure login with RBAC (ADMIN/USER) and 2FA (TOTP)
- Simulated behaviors (dummy data only):
  - Scan and remove viruses: deletes `*.dummy_virus.txt`
  - Speed up computer: mass file copies to simulate slowdown
  - Fix system problems: rename/hide files inside sandbox
- Transparent activity log
- Defense mode: basic detection + quarantine + restore
- Sandbox enforcer prevents non-sandbox execution

## Setup
1) Create virtual env and install:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
