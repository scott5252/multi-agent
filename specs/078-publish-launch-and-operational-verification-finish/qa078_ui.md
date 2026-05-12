# QA078 UI Walkthrough: Publish, Launch, And Operational Verification Finish

## Goal

Validate Publish, Launch, And Operational Verification Finish in the browser at 1280 x 800. This walkthrough references qa078, .env.qa078, and evidence under /tmp/qa078-ui-evidence. What is happening: the reviewer exercises the actual React Admin onboarding wizard. Why this matters: the roadmap is a browser-first workflow setup experience, not an API-only feature.

## How To Use This Guide

1. Use the local login page first.
2. After login, use visible UI links and buttons only.
3. Keep the viewport at 1280 x 800 for no-scroll checks.
4. Capture one screenshot per major step.
5. Record expected and actual results in reviewer notes.
6. Treat backend blockers as valid product states, not test bypasses.
7. Stop if raw unsafe data appears.
8. Stop if the page requires vertical scrolling.

## Environment Setup

```bash
cp specs/078-publish-launch-and-operational-verification-finish/.env.qa078 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: API is reachable and local-principal auth is enabled.

```bash
cd frontend/admin && npm run typecheck
cd frontend/admin && npm test -- WorkflowOnboardingWizardPage workflowSetupWizard ConsoleHomePage App
cd frontend/admin && npm run build
```

Expected: the focused frontend validation passes before manual UI review.

## Browser Walkthrough

### UI Step 1: Local login

What is happening: Open http://127.0.0.1:8000/auth/local-login.

Why this matters: Local login proves the wizard can be operated through visible UI in a constrained frame.

Expected: The local login form shows tenant-admin-acme.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-1.png and note pass or fail.

### UI Step 2: Authenticate

What is happening: Choose tenant-admin-acme.

Why this matters: Authenticate proves the wizard can be operated through visible UI in a constrained frame.

Expected: Console Home renders under Acme tenant scope.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-2.png and note pass or fail.

### UI Step 3: Quick action

What is happening: Find and activate Set up workflow.

Why this matters: Quick action proves the wizard can be operated through visible UI in a constrained frame.

Expected: The wizard opens without manual URL editing.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-3.png and note pass or fail.

### UI Step 4: Scenario

What is happening: Review or enter a neutral workflow name.

Why this matters: Scenario proves the wizard can be operated through visible UI in a constrained frame.

Expected: The name and key are scenario-neutral and editable.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-4.png and note pass or fail.

### UI Step 5: Draft

What is happening: Create or resume a durable draft.

Why this matters: Draft proves the wizard can be operated through visible UI in a constrained frame.

Expected: The mutation result references a backend-owned action summary.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-5.png and note pass or fail.

### UI Step 6: Agents

What is happening: Open the agent step.

Why this matters: Agents proves the wizard can be operated through visible UI in a constrained frame.

Expected: Agent cards or paged entries fit without scrolling.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-6.png and note pass or fail.

### UI Step 7: Contracts

What is happening: Open the contracts step.

Why this matters: Contracts proves the wizard can be operated through visible UI in a constrained frame.

Expected: Contract labels and summaries fit inside their containers.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-7.png and note pass or fail.

### UI Step 8: Graph

What is happening: Open the graph step.

Why this matters: Graph proves the wizard can be operated through visible UI in a constrained frame.

Expected: Node and edge summaries are readable and the footer remains visible.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-8.png and note pass or fail.

### UI Step 9: Resources

What is happening: Open the resource step.

Why this matters: Resources proves the wizard can be operated through visible UI in a constrained frame.

Expected: Provider, skill, channel, prompt, profile, or suite summaries are safe.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-9.png and note pass or fail.

### UI Step 10: Evidence

What is happening: Attach and save required evidence when available.

Why this matters: Evidence proves the wizard can be operated through visible UI in a constrained frame.

Expected: The save action sends a workflow document update and redacted result.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-10.png and note pass or fail.

### UI Step 11: Publish

What is happening: Run validate and publish steps when available.

Why this matters: Publish proves the wizard can be operated through visible UI in a constrained frame.

Expected: Backend blockers or success summaries are truthful.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-11.png and note pass or fail.

### UI Step 12: Launch

What is happening: Open runtime or evidence links.

Why this matters: Launch proves the wizard can be operated through visible UI in a constrained frame.

Expected: Links preserve tenant scope and open visible Admin workspaces.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-12.png and note pass or fail.

### UI Step 13: No-scroll audit

What is happening: Use developer measurement or Playwright assertion for document and wizard body.

Why this matters: No-scroll audit proves the wizard can be operated through visible UI in a constrained frame.

Expected: scrollHeight does not exceed clientHeight for the checked surfaces.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-13.png and note pass or fail.

### UI Step 14: Screenshot review

What is happening: Open saved screenshots.

Why this matters: Screenshot review proves the wizard can be operated through visible UI in a constrained frame.

Expected: No overlapping text, clipped buttons, hidden footer, or unsafe raw data appears.

Reviewer evidence: save screenshot /tmp/qa078-ui-evidence/step-14.png and note pass or fail.

## Required Automated Evidence

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/078-publish-launch-and-operational-verification-finish
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/wizard-ui-roadmap/078-publish-launch-and-operational-verification-finish/validation.yml --start-processes
```

Expected: final roadmap validation passes all automated evidence commands.

## UI Evidence Checklist

- Local login screenshot
- Console Home screenshot with Set up workflow
- Wizard scenario step screenshot
- Draft creation or resume screenshot
- Agents step screenshot
- Contracts step screenshot
- Graph step screenshot
- Resource readiness screenshot
- Evidence step screenshot
- Publish step screenshot
- Launch step screenshot
- No-scroll measurement note
- Redaction review note
- Tenant isolation note
Expected: UI evidence checklist item 1 is captured without unsafe raw values.
Expected: UI evidence checklist item 2 is captured without unsafe raw values.
Expected: UI evidence checklist item 3 is captured without unsafe raw values.
Expected: UI evidence checklist item 4 is captured without unsafe raw values.
Expected: UI evidence checklist item 5 is captured without unsafe raw values.
Expected: UI evidence checklist item 6 is captured without unsafe raw values.
Expected: UI evidence checklist item 7 is captured without unsafe raw values.
Expected: UI evidence checklist item 8 is captured without unsafe raw values.
Expected: UI evidence checklist item 9 is captured without unsafe raw values.
Expected: UI evidence checklist item 10 is captured without unsafe raw values.

## Acceptance Notes Template

```text
QA078 UI acceptance notes
Browser: Chromium
Viewport: 1280 x 800
Principal: tenant-admin-acme
Scenario names: Supplier Risk Intake and Incident Triage
Visible navigation only: pass
No vertical scroll: pass
No text overlap: pass
No unsafe raw data: pass
Backend blocker handling: pass
```

## Troubleshooting

- If local login does not render, restart the API and confirm .env was copied.
- If Set up workflow is absent, confirm workflow registry authorization.
- If the wizard shows loading forever, check /tmp logs and health endpoints.
- If a mutation fails, capture the safe summary and trace id.
- If a screen scrolls, reduce visible content or use pagination.
- If a screenshot shows tutorial-specific defaults, mark the run failed.
- If redaction fails, stop and repair before continuing.
- If Playwright cannot start processes, check PostgreSQL and port 8000 availability.

## Related Files

- specs/078-publish-launch-and-operational-verification-finish/qa078.md
- specs/078-publish-launch-and-operational-verification-finish/.env.qa078
- specs/078-publish-launch-and-operational-verification-finish/qa078_user_guide.md
- frontend/admin/src/components/workflows/WorkflowOnboardingWizardPage.tsx
- frontend/admin/src/styles/admin.css
- specs/_autopilot/wizard-ui-roadmap/078-publish-launch-and-operational-verification-finish/validation.yml
