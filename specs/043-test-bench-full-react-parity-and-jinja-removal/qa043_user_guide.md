# QA043 User Guide: Spec 043 - Test Bench Full React Parity And Jinja Removal

## Detailed Overview

Spec 043 moves the agent and workflow test bench browser experience fully into
the React admin workspace.

The primary route is `/admin/app/test-bench`.

The old browser routes under `/admin/agent-tests/ui` remain as compatibility
entry points only.

Old safe GET routes redirect to React.

Old suite, case, and run form POST routes still call backend behavior before
redirecting to React.

The old `agent_tests` Jinja templates are deleted.

The retained `/admin/agent-tests` JSON API continues to support API clients.

React shows suite definitions, case definitions, run launch controls, run
progress, result diagnostics, trace steps, artifact metadata, publish-gate
evidence, and audit summaries.

The browser does not decide tenant access.

The browser does not decide whether a run is current.

The browser does not decide whether publish-gate evidence is acceptable.

The browser does not execute models, tools, or connectors directly.

The browser does not render raw prompts.

The browser does not render raw completions.

The browser does not render memory contents.

The browser does not render private channel messages.

The browser does not render raw external payloads.

The browser does not render raw artifact contents.

The browser does not render storage paths.

The browser does not render authorization headers.

The local QA environment uses deterministic local-principal authentication.

The local QA environment uses fake `qa043/` secret references.

The local QA environment stores artifacts under `.data/qa043-artifacts`.

The local QA environment blocks live provider probes.

The local QA environment blocks live Telegram delivery.

The local QA environment blocks external connector calls.

Use `platform-admin` for broad platform review.

Use `tenant-admin-acme` for tenant-scoped Acme checks.

Use `tenant-admin-globex` only for cross-tenant denial checks.

Use `tenant-user-acme` to confirm low-privilege users cannot complete protected
actions.

Use `/admin/app/test-bench/bootstrap.json` when you need full dashboard
evidence.

Use `/admin/app/test-bench/suites` when you need suite list evidence.

Use `/admin/app/test-bench/runs.json` when you need run history evidence.

Use `/admin/app/test-bench/runs/run-qa033-failing.json` when you need run detail
evidence.

Use `/admin/app/test-bench/gates.json` when you need publish-gate evidence.

Use `/admin/app/test-bench/artifacts/artifact-qa033-summary.json` when you need
artifact metadata evidence.

Use `/admin/app/test-bench/audit.json` when you need audit timeline evidence.

Do not rely on old Jinja pages as the source of truth.

Do not recreate the deleted templates.

Do not use production tenants.

Do not use production providers.

Do not save evidence that contains secrets.

## Who Should Use This Guide

Use this guide if you are manually reviewing Spec 043.

Use this guide if you need to verify that the React test bench replaces the old
browser pages.

Use this guide if you need to confirm old direct links still behave safely.

Use this guide if you need to collect screenshots for release review.

Use this guide if you are checking tenant isolation or redaction.

Developers can also use this guide to reproduce QA failures locally.

Non-developer reviewers can follow the browser steps and compare expected
results.

Security reviewers should focus on tenant isolation, artifact metadata, gate
evidence, and redaction checks.

## Manual QA Prerequisites

You need the repository checked out locally.

You need Docker available for PostgreSQL.

You need the project dependencies installed through `uv sync`.

You need Node.js and npm available for the React admin build.

You need the QA environment file:

```bash
specs/043-test-bench-full-react-parity-and-jinja-removal/.env.qa043
```

You need local browser access to:

```text
http://127.0.0.1:8000
```

You need screenshot output under:

```bash
output/playwright/qa043_ui
```

You need manual notes under:

```bash
/tmp/qa043-ui-notes.md
```

Expected: all evidence is local to QA043 and does not use production systems.

## Step-by-Step Manual QA

1. Copy the QA environment file.

Command:

```bash
cp specs/043-test-bench-full-react-parity-and-jinja-removal/.env.qa043 .env
```

Expected: `.env` uses `AUTH_MODE=local_principal` and
`multi_agent_platform_qa043`.

2. Install dependencies and build React assets.

Command:

```bash
uv sync
cd frontend/admin && npm run build
cd ../..
```

Expected: Vite writes the React manifest under
`src/multi_agent_platform/web_admin/static/react`.

3. Start PostgreSQL.

Command:

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL container is healthy.

4. Reset only the QA database.

Command:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa043 && createdb -U postgres multi_agent_platform_qa043'
```

Expected: no non-QA database is changed.

5. Apply migrations.

Command:

```bash
uv run alembic upgrade head
```

Expected: migrations finish successfully.

6. Seed Acme and Globex tenants.

Command:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa043 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: both tenants exist.

7. Start the API.

Command:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns successfully.

8. Start the worker in another terminal.

Command:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts without live external calls.

9. Open the local login page.

URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Expected: the login page lists QA principals.

10. Sign in as `platform-admin`.

Expected: the browser lands on `/admin/app/test-bench`.

11. Review the top-level test bench page.

Expected: the page heading is `Test Bench`.

Expected: suite, run, gate, artifact, and audit areas are visible.

Expected: no old Jinja page appears.

12. Review suite authoring.

Expected: suite cards show target type, target id, target revision, required
state, default safe mode, pass threshold, and action availability.

Expected: create-suite controls appear in React.

13. Open the old index link.

URL:

```text
http://127.0.0.1:8000/admin/agent-tests/ui
```

Expected: the browser redirects to `/admin/app/test-bench`.

14. Open the old create-suite link.

URL:

```text
http://127.0.0.1:8000/admin/agent-tests/ui/suites/new?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the browser redirects to React with `mode=create-suite`.

15. Review case authoring.

Expected: fixture, expected contract shape, and assertion controls are visible
as React controls.

Expected: unsafe raw workflow payloads are not visible.

16. Launch a safe run if the action is enabled.

Expected: use a mocked or side-effect-disabled mode.

Expected: the mutation result includes a safe run id and audit reference.

17. Review run detail.

URL:

```text
http://127.0.0.1:8000/admin/app/test-bench?run_id=run-qa033-failing
```

Expected: diagnostics, trace steps, artifact references, gate status, and
remediation text are visible.

Expected: raw prompts, raw completions, and memory contents are not visible.

18. Open the old run detail link.

URL:

```text
http://127.0.0.1:8000/admin/agent-tests/ui/runs/run-qa033-failing?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the browser redirects to React with `run_id=run-qa033-failing`.

19. Review artifact metadata.

URL:

```text
http://127.0.0.1:8000/admin/app/test-bench?artifact_reference_id=artifact-qa033-summary
```

Expected: the screen shows artifact label, classification, checksum, status,
and authorized link metadata.

Expected: raw artifact bodies and storage paths are absent.

20. Review publish-gate evidence.

URL:

```text
http://127.0.0.1:8000/admin/app/test-bench?gate_id=gate-qa033-stale
```

Expected: stale, missing, failed, passed, audit unavailable, and redaction
unavailable states are understandable.

Expected: each state has reason and remediation text.

21. Review audit evidence.

URL:

```text
http://127.0.0.1:8000/admin/app/test-bench?audit_ref=audit-gate-qa033-passed
```

Expected: audit events show safe actor, action, target, status, and reference
summaries.

22. Switch to `tenant-admin-acme`.

URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the browser lands on an Acme-scoped test bench view.

23. Attempt a Globex-scoped old URL while signed in as Acme.

URL:

```text
http://127.0.0.1:8000/admin/agent-tests/ui?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: the request fails closed or shows a safe denial.

Expected: Globex private data is not visible.

24. Capture screenshots.

Expected: capture the test bench home, run detail, artifact metadata, gate
evidence, legacy redirect result, and cross-tenant denial.

25. Save reviewer notes.

Expected: notes are written to `/tmp/qa043-ui-notes.md`.

## Expected Results

The React route `/admin/app/test-bench` loads successfully.

The page heading is `Test Bench`.

The old `/admin/agent-tests/ui` route redirects to React.

The old `/admin/agent-tests/ui/suites/new` route preserves `tenant_id` and
`mode=create-suite`.

The old `/admin/agent-tests/ui/runs/run-qa033-failing` route preserves `run_id`
after authorization.

Suite and case authoring are available in React.

Safe run launch is available through backend mutation endpoints.

Run diagnostics show safe summaries.

Artifact detail is metadata-only.

Publish-gate evidence clearly distinguishes current and stale state.

Audit evidence is redacted.

Cross-tenant requests fail closed.

Deleted Jinja templates are not rendered.

## Evidence To Capture

Capture a screenshot of the React test bench home page.

Capture a screenshot of the suite authoring area.

Capture a screenshot of the run detail page.

Capture a screenshot of artifact metadata.

Capture a screenshot of publish-gate evidence.

Capture a screenshot of audit evidence.

Capture a screenshot or notes for old route redirects.

Capture a screenshot or notes for cross-tenant denial.

Save command output from focused backend tests.

Save command output from frontend tests.

Save Playwright output from `qa043-react-ui2-smoke.png`.

## Security And Redaction Checks

Search the page for `raw prompt`.

Search the page for `raw completion`.

Search the page for `memory contents`.

Search the page for `private channel`.

Search the page for `raw external`.

Search the page for `raw tool output`.

Search the page for `authorization header`.

Search the page for `resolved credential`.

Search the page for `storage path`.

Search the page for `/Users/`.

Expected: none of these strings appear in visible React text.

Expected: artifact pages show metadata and checksums only.

Expected: run pages show summaries and remediation only.

Expected: gate pages show status, reason, target revision, and safe audit
references only.

## Tenant Isolation Checks

Sign in as `tenant-admin-acme`.

Open `/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111`.

Expected: Acme-scoped data is visible.

Open `/admin/agent-tests/ui?tenant_id=22222222-2222-2222-2222-222222222222`.

Expected: the request fails closed or returns a safe denial.

Expected: Globex private suite, case, run, artifact, and gate data are not
visible.

Sign in as `tenant-admin-globex`.

Open an Acme suite or run link from notes.

Expected: the request fails closed.

Expected: Acme private data is not visible.

## Troubleshooting

If `/admin/app/test-bench` returns `401`, sign in through local login again.

If `/admin/app/test-bench` returns a blank page, rebuild React assets.

If old URLs return HTML with an old test bench layout, stop and inspect
`admin_agent_tests.py`.

If a tenant link returns `403`, confirm the selected principal owns that tenant.

If Playwright cannot find `Test Bench`, confirm `validation.yml` points to
`/admin/app/test-bench`.

If run detail is empty, confirm the URL includes the expected `run_id`.

If artifact metadata shows raw content, stop and preserve the evidence.

If gate evidence does not show stale or unavailable states, inspect the backend
test bench evidence builder.

If any redaction marker appears, treat it as a blocking defect.
