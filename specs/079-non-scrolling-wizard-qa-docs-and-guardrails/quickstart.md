# Quickstart: Non-Scrolling Wizard QA, Docs, And Guardrails

## Local Setup

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
cd frontend/admin && npm ci
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/auth/local-login and choose tenant-admin-acme. Use visible UI controls to reach Console Home and the Set up workflow action.

## Focused Validation

```bash
cd frontend/admin && npm test -- WorkflowOnboardingWizardPage workflowSetupWizard ConsoleHomePage App
cd frontend/admin && npm run typecheck
cd frontend/admin && npm run build
uv run python scripts/frontend/generate_admin_react_types.py --check
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/079-non-scrolling-wizard-qa-docs-and-guardrails
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/wizard-ui-roadmap/079-non-scrolling-wizard-qa-docs-and-guardrails/validation.yml --skip-quality
```

## Browser Path

1. Sign in with tenant-admin-acme.
2. On Console Home, select Set up workflow.
3. Confirm the wizard frame renders without vertical scroll at 1280 x 800.
4. Move through the steps relevant to this spec slice.
5. Save, validate, publish, or open handoff links only through visible controls.
6. Capture screenshots and reviewer notes under the QA artifact directory.
