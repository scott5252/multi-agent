# QA057 UI: Operations And Run Debug React Live Data

## Goal

Guide a reviewer through browser evidence for qa057.

Expected: the React operations workbench loads live backend records.

Expected: Acme shows seeded health, run-debug, gateway, tool, delivery, likely
cause, reliability, log, and export evidence.

Expected: Globex shows a truthful empty state.

Expected: clicking `Export evidence` persists backend audit/export metadata.

Expected: the browser never shows raw secrets, credential values, authorization
headers, prompts, completions, memory content, raw run details, private
messages, connector details, local paths, stack traces, unauthorized tenant
labels, or old QA029 artifact references.

What is happening: the page is using `/admin/app/operations.json`,
`/admin/app/operations/runs/{workflow_run_id}.json`, and
`/admin/app/operations/export` rather than fixed production helper rows.

Why this matters: qa057 is only done if browser-visible operations triage is
backed by the same database rows the API and verifier inspect.

## How To Use This Guide

Use this walkthrough with `qa057.md`.

Save screenshots under `output/playwright/qa057_ui`.

Save reviewer notes under `/tmp/qa057-ui-reviewer-notes.txt`.

Save browser console notes under `/tmp/qa057-ui-console-notes.txt`.

Save post-action API notes under `/tmp/qa057-ui-post-api-notes.txt`.

Save verifier output under `/tmp/qa057-ui-verifier-output.txt`.

Expected: screenshot filenames include qa057.

Expected: notes mention the local principal and tenant being reviewed.

Expected: API notes identify exports by `operations-export:UUID` only.

Expected: reviewer notes avoid copying unsafe payload content.

What is happening: automated Playwright follows the same export-centered flow.

Why this matters: manual evidence and automated evidence should match.

## Environment Setup

Copy the QA environment.

```bash
cp specs/057-operations-and-run-debug-react-live-data/.env.qa057 .env
```

Expected: `.env` now contains `APP_NAME=multi-agent-platform-qa057`.

Install dependencies.

```bash
uv sync
npm install --prefix frontend/admin
```

Expected: dependencies are available.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL service is running.

Reset the qa057 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa057 && createdb -U postgres multi_agent_platform_qa057'
```

Expected: only the qa057 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete successfully.

Seed operations records.

```bash
uv run python scripts/qa/seed_operations_qa057.py
```

Expected: the command prints `Seeded QA057 operations live records`.

Create output directories.

```bash
mkdir -p output/playwright/qa057_ui .data/qa057-artifacts
```

Expected: screenshot and artifact directories exist.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

Start the worker in another terminal for full local evidence.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts in local QA mode without external calls.

## Browser Walkthrough

1. Open local login.

URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-admin-acme`.

Expected: the browser redirects to the Operations workbench.

What is happening: the local principal cookie scopes the browser session to the
Acme tenant admin.

Why this matters: tenant-admin output must be scoped before any live evidence
is displayed.

2. Review the page header.

URL: `http://127.0.0.1:8000/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: look for the Operations heading and freshness label.

Expected: the page title is `Operations workbench`.

Expected: the header shows `Last 60 minutes`.

Expected: the generated label starts with `Generated from live evidence`.

What is happening: the React page loaded the backend-owned workbench contract.

Why this matters: a deterministic QA029 label would mean the old projection is
still visible.

3. Review summary cards.

Action: inspect the card grid.

Expected: Acme shows `Tenant live evidence`.

Expected: platform-only provider, database, worker, queue, and storage pressure
does not appear in the tenant card grid.

Expected: the tenant activity panel explains that platform-only pressure is
hidden.

What is happening: the workbench filtered live evidence to the tenant scope.

Why this matters: tenant admins must not see shared infrastructure pressure
unless a safe policy explicitly allows it.

4. Review likely causes.

Action: inspect the Likely causes panel.

Expected: the panel references the live gateway timeout symptom.

Expected: the recommendation points to safe diagnostics, not a raw event body.

What is happening: likely causes are derived deterministically from live
symptoms.

Why this matters: no live model call or raw payload inspection is needed to
produce triage guidance.

5. Review run debug.

Action: inspect the Run debug timeline and diagnostic grids.

Expected: the run title references workflow run `57000000`.

Expected: timeline rows, gateway attempts, tool calls, and delivery rows are
present.

Expected: the tool call shows `allowed_read_only`.

Expected: the delivery row shows a retry state without private message text.

What is happening: the run-debug projection is resolving the seeded run from
audit, runtime trace, and gateway rows.

Why this matters: direct run-debug links must never fall back to a fixed run.

6. Create an export.

Action: click `Export evidence`.

Expected: the export panel updates to `complete`.

Expected: the artifact field starts with `operations-export:`.

Expected: the row count is greater than zero.

Expected: no `file:` URI, storage URL, or local path appears.

What is happening: the browser posts to `/admin/app/operations/export` and the
backend writes storage plus audit metadata.

Why this matters: reviewer evidence must be durable, scoped, and safe.

7. Verify export persistence.

Action: run the verifier.

```bash
uv run python scripts/qa/verify_operations_qa057.py | tee /tmp/qa057-ui-verifier-output.txt
```

Expected: verifier output includes `browser_export_reference=operations-export:`.

Expected: verifier output includes `browser_export_checksum=sha256:`.

What is happening: the verifier checks the same database used by the browser.

Why this matters: browser state alone is not enough evidence for this spec.

8. Switch to Globex.

URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations?tenant_id=22222222-2222-2222-2222-222222222222`

Action: choose `tenant-admin-globex`.

Expected: the browser opens the Operations workbench for Globex.

Expected: the first summary card is an empty live evidence state.

Expected: logs and run debug are empty.

Expected: Acme and the seeded run ID do not appear.

What is happening: Globex has a tenant record but no seeded operational rows.

Why this matters: empty live databases must stay honest and must not invent
incidents.

9. Check cross-tenant denial.

URL: `http://127.0.0.1:8000/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: while signed in as `tenant-admin-globex`, try to open the Acme URL.

Expected: access is denied.

Expected: the response does not reveal Acme operational labels.

What is happening: the shell scope resolver fails closed before building the
workbench payload.

Why this matters: tenant isolation must be enforced before rendering.

10. Save screenshots.

Action: save screenshots of Acme seeded view, export result, and Globex empty
view.

Expected: screenshots are stored under `output/playwright/qa057_ui`.

Expected: screenshots do not include forbidden content or old QA029 labels.

What is happening: screenshots become review evidence for the spec.

Why this matters: visual evidence must be safe enough to share with reviewers.

## Required Automated Evidence

Run focused backend tests.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_workbench_schema.py tests/unit/operations/test_workbench_service.py tests/integration/test_admin_react_routes.py -k 'workbench or react_admin_operations' -q
```

Expected: focused backend tests pass.

Run frontend checks.

```bash
npm run --prefix frontend/admin test -- --run Workbench
npm run --prefix frontend/admin typecheck
```

Expected: Workbench component tests and TypeScript checks pass.

Run required project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all project-wide gates pass before review.

Run Spec QA and browser automation.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml --start-processes
uv run python scripts/qa/verify_operations_qa057.py
```

Expected: Spec QA, Playwright, and post-UI verifier pass.

## UI Evidence Checklist

- Acme seeded workbench screenshot saved.
- Acme run-debug timeline screenshot saved.
- Export result screenshot saved.
- Globex empty-state screenshot saved.
- Verifier output saved.
- Browser console checked for errors.
- Redaction grep completed.
- No QA029 label or artifact reference visible.

## Acceptance Notes Template

Reviewer:

Date:

Principal used first:

Acme screenshot:

Export screenshot:

Globex screenshot:

Verifier output:

Result:

Notes:

## Troubleshooting

If the page stays on loading, check API logs and confirm `.env` points to
`multi_agent_platform_qa057`.

If Acme has no logs, rerun the seed script and refresh the page.

If export remains `empty`, confirm the `Export evidence` button click reached
the backend and check the network panel.

If export status is `unavailable`, confirm `.data/qa057-artifacts` is writable.

If Globex shows Acme rows, stop and treat it as a tenant-isolation blocker.

If screenshots contain old QA029 labels, rebuild React assets and rerun the
workbench tests.

## Related Files

- `specs/057-operations-and-run-debug-react-live-data/qa057.md`
- `specs/057-operations-and-run-debug-react-live-data/.env.qa057`
- `scripts/qa/seed_operations_qa057.py`
- `scripts/qa/verify_operations_qa057.py`
- `src/multi_agent_platform/operations/workbench.py`
- `frontend/admin/src/components/workbench/`
- `output/playwright/qa057_ui`
