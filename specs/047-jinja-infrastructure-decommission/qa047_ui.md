# QA047 UI Walkthrough

## Goal

Verify a local-principal reviewer can use the React-only browser UI after server-side template infrastructure is removed. What is happening: the browser receives React-hosted pages, static local-login HTML, or safe redirects. Why this matters: the final migration must be visible and usable without any template renderer.

## How To Use This Guide

Start the app through the QA runner or manually with .env.qa047. Capture screenshots and reviewer notes under /tmp/qa047-ui-notes.txt and output/playwright/qa047_ui.

## Environment Setup

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/047-jinja-infrastructure-decommission/.env.qa047 .env
uv sync
cd frontend/admin && npm run build && cd ../..
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected: app starts with AUTH_MODE=local_principal and React assets available.

What is happening: FastAPI serves React static assets and non-template local login HTML.
Why this matters: this proves browser delivery does not depend on server-side templates.

## Browser Walkthrough

### 1. Open local login

Action: http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration

Expected: the local login page lists platform-admin and tenant-admin-acme without a deleted CSS request.

What is happening: Open local login exercises React or non-template compatibility behavior.

Why this matters: Open local login is part of the final browser decommission proof.

### 2. Sign in as platform-admin

Action: Click platform-admin Sign In

Expected: browser lands on /admin/app/migration and shows React-only browser UI.

What is happening: Sign in as platform-admin exercises React or non-template compatibility behavior.

Why this matters: Sign in as platform-admin is part of the final browser decommission proof.

### 3. Review decommission heading

Action: Read the migration header and summary metrics

Expected: retained fallback count is zero and next step mentions React-only browser UI.

What is happening: Review decommission heading exercises React or non-template compatibility behavior.

Why this matters: Review decommission heading is part of the final browser decommission proof.

### 4. Review decommission inventory

Action: Scroll to React-only readiness

Expected: no server-rendered inventory rows remain for this scope.

What is happening: Review decommission inventory exercises React or non-template compatibility behavior.

Why this matters: Review decommission inventory is part of the final browser decommission proof.

### 5. Review route matrix

Action: Inspect route compatibility rows

Expected: operations and workflow links appear as redirects or aliases, not template pages.

What is happening: Review route matrix exercises React or non-template compatibility behavior.

Why this matters: Review route matrix is part of the final browser decommission proof.

### 6. Review rollback panel

Action: Inspect Route safety plan

Expected: Release rollback explains redeploying the previous reviewed release.

What is happening: Review rollback panel exercises React or non-template compatibility behavior.

Why this matters: Review rollback panel is part of the final browser decommission proof.

### 7. Review tenant scope

Action: Open /auth/local-login?redirect_to=/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111 and sign in as tenant-admin-acme

Expected: platform-only rows are hidden and no Globex label appears.

What is happening: Review tenant scope exercises React or non-template compatibility behavior.

Why this matters: Review tenant scope is part of the final browser decommission proof.

### 8. Open user run workspace

Action: Open /auth/local-login?redirect_to=/runs and sign in as tenant-admin-acme

Expected: /runs redirects to /admin/app/channels/runs and shows Run workspace.

What is happening: Open user run workspace exercises React or non-template compatibility behavior.

Why this matters: Open user run workspace is part of the final browser decommission proof.

### 9. Start a run

Action: Click Start Run

Expected: run accepted through channel facade appears with safe status and timeline sections.

What is happening: Start a run exercises React or non-template compatibility behavior.

Why this matters: Start a run is part of the final browser decommission proof.

### 10. Capture screenshot

Action: Save screenshot through Playwright or browser tooling

Expected: evidence file is output/playwright/qa047_ui/qa047-react-ui2-smoke.png.

What is happening: Capture screenshot exercises React or non-template compatibility behavior.

Why this matters: Capture screenshot is part of the final browser decommission proof.

## Required Automated Evidence

```bash
uv run ruff check .
```
Expected: Ruff check passes.

```bash
uv run ruff format --check .
```
Expected: Format check passes.

```bash
uv run mypy src
```
Expected: mypy passes.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
Expected: full coverage gate passes.

```bash
cd frontend/admin && npm test -- --run src/components/migrationHardening src/App.test.tsx
```
Expected: migration hardening and App tests pass.

```bash
cd frontend/admin && npm run typecheck && npm run build
```
Expected: frontend typecheck and build pass.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml --start-processes
```
Expected: Playwright creates screenshot evidence under output/playwright/qa047_ui.

## UI Evidence Checklist

- Expected: UI evidence 1 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 1 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 2 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 2 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 3 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 3 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 4 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 4 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 5 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 5 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 6 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 6 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 7 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 7 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 8 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 8 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 9 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 9 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 10 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 10 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 11 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 11 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 12 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 12 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 13 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 13 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 14 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 14 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 15 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 15 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 16 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 16 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 17 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 17 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 18 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 18 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 19 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 19 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 20 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 20 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 21 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 21 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 22 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 22 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 23 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 23 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.
- Expected: UI evidence 24 references qa047, shows React-only or safe redirect behavior, and avoids raw prompts, raw payloads, full external identifiers, local paths, stack traces, and unauthorized tenant labels. What is happening: reviewer evidence 24 checks a visible browser state. Why this matters: repeated evidence catches copy, routing, and redaction regressions.

## Acceptance Notes Template

- Reviewer:
- Date:
- Browser:
- Screenshot path: output/playwright/qa047_ui/qa047-react-ui2-smoke.png
- Notes path: /tmp/qa047-ui-notes.txt
- Expected: React-only browser UI observed.
- Expected: Run workspace observed from /runs redirect.

## Troubleshooting

If /admin/app/migration shows stale copy, rebuild frontend/admin and confirm generated assets changed. If local login has missing CSS requests, inspect src/multi_agent_platform/api/routers/auth.py. If /runs does not redirect, rerun focused web_run_ui tests. If tenant scope leaks Globex data into Acme views, stop and fix backend scope validation.

## Related Files

- specs/047-jinja-infrastructure-decommission/qa047.md
- specs/047-jinja-infrastructure-decommission/.env.qa047
- specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml
- frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx
- frontend/admin/src/components/userRuns/UserRunPage.tsx
