# Ethics & Safety Controls

## Disclaimer (MANDATORY)
Educational simulation - all actions reversible

## Safety Controls Implemented
1) Sandbox Enforcer / Directory Whitelisting
- All file actions are validated to remain under SANDBOX_ROOT using realpath checks.
- Requests targeting paths outside SANDBOX_ROOT are refused.

2) Kill Switch
- If SANDBOX_ROOT/.kill exists, simulation endpoints refuse to execute.

3) Auto-disable after 24 hours
- On first run, SANDBOX_ROOT/.created_at is created.
- If the current time exceeds created_at + 24 hours, simulation endpoints refuse to execute.

4) Reversibility
- Actions are performed on dummy files only.
- Defense restore returns quarantined/moved files to original locations.

## Non-Distribution
This repository must not be packaged or distributed outside educational context.
