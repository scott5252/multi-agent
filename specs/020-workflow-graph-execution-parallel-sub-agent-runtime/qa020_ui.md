# QA020 UI Walkthrough: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Goal

Give browser reviewers a clear path for validating the user-visible parts of
Spec 020 while the graph execution behavior is verified by deterministic
automated tests.

Spec 020 is mainly a runtime and worker feature. The manual browser evidence
therefore focuses on the shared admin shell, local-principal login, run
inspection surfaces, operations readiness, and safe reviewer notes that connect
the browser state to the graph execution evidence.

The walkthrough uses `qa020`, `.env.qa020`, the isolated
`multi_agent_platform_qa020` database, and local screenshots saved under
`output/playwright/qa020_ui`.

## How To Use This Guide

Use this file after the implementation tests in `qa020.md` pass.

Use one browser window and two terminal windows.

Terminal A starts the API.

Terminal B runs setup commands, validation commands, and focused tests.

The browser steps are intentionally light because Spec 020 does not introduce a
new admin form. They prove that the graph-enabled worker still fits inside the
existing admin and run-inspection experience.

For every screen, capture a screenshot or reviewer note that includes:

- the URL
- the signed-in local principal
- the tenant scope when visible
- the visible safe state
- the time of the capture
- whether raw secrets or raw graph payloads were visible

## Environment Setup

### UI Setup Step 1 - Copy The QA Environment

```bash
cp specs/020-workflow-graph-execution-parallel-sub-agent-runtime/.env.qa020 .env
mkdir -p .data/qa020-artifacts output/playwright/qa020_ui
```

Expected: the commands complete without output.

What is happening: the API, worker, storage, and browser evidence paths are
pointed at QA020-only resources.

Why this matters: the reviewer should never need shared developer settings to
inspect Spec 020.

### UI Setup Step 2 - Reset And Migrate The Database

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa020 && createdb -U postgres multi_agent_platform_qa020'
uv run alembic upgrade head
```

Expected: PostgreSQL starts, the QA020 database is reset, and Alembic reaches
head.

What is happening: the browser session will use the same schema as the
automated graph execution tests.

Why this matters: runtime rows, timeline events, approval gates, and worker
leases must render through existing admin pages without new migrations.

### UI Setup Step 3 - Start The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the API listens on `http://127.0.0.1:8000`.

What is happening: the browser will hit the local FastAPI application.

Why this matters: local-principal auth and shared admin navigation are part of
the reviewer contract.

### UI Setup Step 4 - Optional Worker Startup

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts and polls for runnable workflow runs.

What is happening: the graph-enabled worker imports the same runtime service
used by the focused integration tests.

Why this matters: the browser can be used alongside worker logs when reviewing
claim and status evidence.

## Browser Walkthrough

### Browser Step 1 - Open Local Login

Open this URL:

[http://127.0.0.1:8000/auth/local-login](http://127.0.0.1:8000/auth/local-login)

Expected: the local-principal login page lists QA principals such as
`platform-admin`, `tenant-admin-acme`, `operator-acme`, and
`tenant-admin-globex`.

What is happening: the app is reading local users from `.env.qa020`.

Why this matters: QA020 must be reviewable without Auth0 tokens or real
credentials.

Capture evidence: screenshot the login page before selecting a user.

### Browser Step 2 - Sign In As Platform Admin

Open this URL:

[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin)

Select `platform-admin`.

Expected: the browser lands on `/admin` and shows the shared admin shell.

What is happening: the platform-level principal is authenticated by the
local-principal cookie.

Why this matters: platform administrators must still reach operational
inspection pages after the worker graph runtime is added.

Capture evidence: screenshot the admin shell and note the selected principal.

### Browser Step 3 - Review Workflow Studio Navigation

Open:

[http://127.0.0.1:8000/admin/workflows/ui](http://127.0.0.1:8000/admin/workflows/ui)

Expected: the workflow studio loads with the normal draft and published bundle
navigation.

What is happening: Spec 020 consumes published workflow version bundles that
are authored and published by the existing workflow registry.

Why this matters: graph execution must stay compatible with published bundle
metadata rather than adding a separate authoring surface.

Capture evidence: screenshot the workflow studio landing state.

### Browser Step 4 - Review Run Inspection Navigation

Open:

[http://127.0.0.1:8000/admin/runs](http://127.0.0.1:8000/admin/runs)

Expected: the run inspection page renders a safe list or empty state.

What is happening: run timeline, step, approval, handoff, and side-effect
evidence remain available through existing admin run inspection.

Why this matters: graph execution evidence must be inspectable without showing
raw secrets, prompts, model responses, or tool payloads.

Capture evidence: screenshot the run inspection state. If a seeded graph run is
visible, note whether the displayed summaries are safe.

### Browser Step 5 - Review Operations Console

Open:

[http://127.0.0.1:8000/admin/operations](http://127.0.0.1:8000/admin/operations)

Expected: the operations console renders health and dependency readiness, or a
safe empty or dependency-warning state if optional services are missing.

What is happening: QA020 exercises shared operational surfaces that reviewers
use during worker validation.

Why this matters: the graph worker must not break broader operational status
visibility.

Capture evidence: screenshot the operations page and note any local dependency
warning exactly as displayed.

### Browser Step 6 - Tenant Admin Acme Login

Open:

[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin)

Select `tenant-admin-acme`.

Expected: the browser returns to `/admin` with Acme tenant context available on
tenant-aware pages.

What is happening: a tenant-scoped reviewer signs in using local-principal
metadata.

Why this matters: graph runs must stay tenant-isolated when viewed by tenant
reviewers.

Capture evidence: screenshot the admin shell after switching principal.

### Browser Step 7 - Tenant Isolation Spot Check

While signed in as `tenant-admin-acme`, open:

[http://127.0.0.1:8000/admin/runs](http://127.0.0.1:8000/admin/runs)

Expected: Acme can view only authorized run information or a safe empty state.

What is happening: the UI applies the same tenant boundary that the graph
executor enforces when loading published bundles.

Why this matters: cross-tenant execution denial must be matched by
cross-tenant inspection denial.

Capture evidence: screenshot the page and add a reviewer note that Globex data
was not visible.

### Browser Step 8 - Tenant Admin Globex Login

Open:

[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin)

Select `tenant-admin-globex`.

Expected: the browser returns to `/admin` with Globex tenant context available
on tenant-aware pages.

What is happening: the reviewer uses a second tenant identity from `.env.qa020`.

Why this matters: QA020 must prove both sides of the tenant boundary.

Capture evidence: screenshot the admin shell after switching principal.

### Browser Step 9 - Safe Evidence Review

Return to the screenshots captured in steps 1 through 8.

Expected: no screenshot contains raw secrets, raw credential values, raw prompt
text, raw model responses, raw tool payloads, or unauthorized tenant data.

What is happening: the reviewer is checking the browser surface for the same
redaction guarantees covered by integration tests.

Why this matters: graph runtime evidence is useful only when it is safe for
reviewers and auditors.

Capture evidence: record a short reviewer note naming every screenshot file
and confirming the redaction result.

### Browser Step 10 - Automated Browser Smoke

Run:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml --start-processes
```

Expected: Playwright starts configured processes, finds no feature-specific
flows to run, and exits successfully.

What is happening: Spec 020 currently has no new browser workflow to automate,
but the harness still proves the browser validation path is configured.

Why this matters: later UI additions can add flows without changing the QA020
validation contract.

## Required Automated Evidence

Run these commands before accepting the UI walkthrough:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/020-workflow-graph-execution-parallel-sub-agent-runtime
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml --start-processes
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: every command exits successfully.

What is happening: documentation, API health, process startup, browser smoke,
linting, formatting, static typing, and full coverage are verified together.

Why this matters: UI evidence is only accepted when the runtime implementation
also passes the repository gates.

## UI Evidence Checklist

- Screenshot: local login page shows QA principals.
- Screenshot: `/admin` as `platform-admin`.
- Screenshot: `/admin/workflows/ui` as `platform-admin`.
- Screenshot: `/admin/runs` as `platform-admin`.
- Screenshot: `/admin/operations` as `platform-admin`.
- Screenshot: `/admin` as `tenant-admin-acme`.
- Screenshot: `/admin/runs` as `tenant-admin-acme`.
- Screenshot: `/admin` as `tenant-admin-globex`.
- Reviewer note: no screenshot exposes raw secrets.
- Reviewer note: no screenshot exposes raw prompt or model response content.
- Reviewer note: no screenshot exposes raw tool payloads.
- Reviewer note: no screenshot exposes unauthorized tenant data.
- Reviewer note: focused graph tests passed before browser review.
- Reviewer note: Playwright smoke completed.

## Acceptance Notes Template

```text
QA020 UI reviewer:
Date:
Browser:
Local principal sequence: platform-admin, tenant-admin-acme, tenant-admin-globex
Login screenshot: PASS or FAIL
Admin shell screenshot: PASS or FAIL
Workflow studio screenshot: PASS or FAIL
Run inspection screenshot: PASS or FAIL
Operations screenshot: PASS or FAIL
Tenant isolation note: PASS or FAIL
Redaction note: PASS or FAIL
Playwright smoke: PASS or FAIL
Evidence folder: output/playwright/qa020_ui
Notes:
```

Expected: reviewers fill in the template with actual evidence.

What is happening: screenshots and notes are tied to the same acceptance
language used by the automated QA.

Why this matters: manual review stays repeatable even when the visible browser
state is mostly shared platform UI.

## Troubleshooting

- If the login page does not list QA users, confirm `.env.qa020` was copied to
  `.env` and restart the API.
- If `/admin` redirects unexpectedly, clear the local-principal cookie and
  sign in again through `/auth/local-login`.
- If `/admin/operations` shows dependency warnings, compare them with
  `/dependencies` before treating them as regressions.
- If `/admin/runs` is empty, rely on the focused integration tests for graph
  run evidence and record the empty state screenshot.
- If a screenshot exposes raw sensitive values, stop review and run the
  redaction-focused tests from `qa020.md`.
- If Playwright cannot start the API, inspect `/tmp/qa020-api.log`.
- If Playwright cannot start the worker, inspect `/tmp/qa020-worker.log`.
- If port `8000` is busy, stop the conflicting local process before rerunning
  the validation script.

## Related Files

- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_user_guide.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/testing-instructions.md`
- `specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml`
- `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- `src/multi_agent_platform/workers/orchestration.py`
- `tests/integration/runtime/test_workflow_graph_execution.py`
- `tests/integration/workers/test_orchestration_worker.py`
