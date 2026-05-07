# QA043 UI: Spec 043 - Test Bench Full React Parity And Jinja Removal

## Goal

This UI walkthrough verifies the browser experience for Spec 043.

The reviewer should confirm that the agent and workflow test bench now runs in
the React admin workspace, that old `/admin/agent-tests/ui...` links redirect
there safely, and that deleted `agent_tests` Jinja templates are not needed for
suite authoring, case authoring, run launch, run progress, diagnostics,
artifact metadata, gate evidence, or audit review.

Use this document even if you are not a developer.

Expected: by the end of the walkthrough, the reviewer has screenshots and notes
proving React parity, direct-link compatibility, tenant isolation, stale gate
handling, metadata-only artifacts, and redaction-safe diagnostics.

## How To Use This Guide

Follow the sections in order.

Keep browser screenshots under `output/playwright/qa043_ui`.

Keep manual reviewer notes under `/tmp/qa043-ui-notes.md`.

Use local-principal login only.

Do not enter real provider credentials, real Telegram tokens, real Auth0
values, real connector credentials, private messages, raw prompts, raw
completions, memory contents, or external payloads.

Expected: all UI checks are deterministic and safe to share.

What is happening: the React UI reads backend-owned test bench contracts and
displays safe summaries.

Why this matters: the UI must prove parity without recreating tenant,
publication, execution, artifact, or redaction decisions in the browser.

## Environment Setup

Copy the QA environment.

```bash
cp specs/043-test-bench-full-react-parity-and-jinja-removal/.env.qa043 .env
```

Expected: `.env` points at `multi_agent_platform_qa043`,
`.data/qa043-artifacts`, and `AUTH_MODE=local_principal`.

Install dependencies and build React assets.

```bash
uv sync
cd frontend/admin && npm run build
cd ../..
```

Expected: dependencies are ready and the React manifest references the latest
admin bundle.

Start PostgreSQL and reset the QA database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa043 && createdb -U postgres multi_agent_platform_qa043'
uv run alembic upgrade head
```

Expected: the database is reset and migrations complete.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa043 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist for role and tenant-scope checks.

Start the API and worker.

```bash
mkdir -p output/playwright/qa043_ui /tmp/qa043-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa043-ui/api.log 2>&1
```

Expected: the API serves `http://127.0.0.1:8000/health/live`.

In another terminal, start the worker.

```bash
uv run python -m multi_agent_platform.workers.main > /tmp/qa043-ui/worker.log 2>&1
```

Expected: the worker runs without live provider, Telegram, credential,
connector, model, or external tool calls.

Open the browser login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Expected: the local login page lists `platform-admin`, `tenant-admin-acme`, and
other QA principals.

## Browser Walkthrough

1. Sign in as `platform-admin`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench`

Action: choose `platform-admin`.

Expected: the browser lands on `/admin/app/test-bench`.

What is happening: the local-principal login writes a safe local auth cookie for
the platform admin.

Why this matters: platform reviewers need access to global test bench evidence
without production Auth0.

2. Review the test bench landing page.

Page URL: `http://127.0.0.1:8000/admin/app/test-bench`

Action: capture `output/playwright/qa043_ui/manual-test-bench-home.png`.

Expected: the page heading is `Test Bench`, and suite, run, diagnostics,
artifact, publish-gate, audit, and legacy redirect context is visible.

What is happening: the React page loads `bootstrap.json` and renders
backend-owned summaries.

Why this matters: the first screen replaces the old test bench Jinja index.

3. Review suite authoring.

Page URL: `/admin/app/test-bench`

Action: inspect the suite list and create-suite controls.

Expected: suite cards show target type, target id, target revision, safe mode,
pass threshold, required-for-publish state, and action availability.

What is happening: React renders suite metadata from backend test bench
contracts.

Why this matters: suite authoring must remain possible after the old form
template is deleted.

4. Open the old test bench index URL.

Page URL: `http://127.0.0.1:8000/admin/agent-tests/ui`

Action: paste the URL into the address bar.

Expected: the browser redirects to `/admin/app/test-bench`.

What is happening: the old route authenticates and issues a React redirect.

Why this matters: legacy direct links no longer render Jinja.

5. Open the old create-suite URL with tenant scope.

Page URL: `/admin/agent-tests/ui/suites/new?tenant_id=11111111-1111-1111-1111-111111111111`

Action: paste the URL while signed in.

Expected: the browser redirects to
`/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111&mode=create-suite`.

What is happening: the redirect preserves tenant and create intent.

Why this matters: bookmarked create links must remain useful after template
removal.

6. Review case authoring.

Page URL: `/admin/app/test-bench?mode=create-case&suite_id=suite-qa033-daily-briefing`

Action: inspect fixture, expected contract shape, assertion, and validation
states.

Expected: fixture and assertion inputs are controlled by React and summarize
safe content only.

What is happening: React displays case authoring state without server-rendered
form fields.

Why this matters: test cases may involve workflow expectations and must not
render private payloads.

7. Launch a safe run if the action is enabled.

Page URL: `/admin/app/test-bench?suite_id=suite-qa033-daily-briefing`

Action: choose a mocked or side-effect-disabled mode and launch the run.

Expected: the mutation result shows an accepted run, an audit reference, and a
React link containing `run_id`.

What is happening: the browser posts to a backend-owned run launch endpoint.

Why this matters: React must not execute models, tools, or connectors directly.

8. Review run progress and diagnostics.

Page URL: `/admin/app/test-bench?run_id=run-qa033-failing`

Action: inspect status, case summaries, step timeline, failure diagnostics, and
safe remediation text.

Expected: the detail view shows pass/fail state and diagnostic summaries without
raw prompt, completion, memory, or external tool payloads.

What is happening: React fetches `/admin/app/test-bench/runs/run-qa033-failing.json`.

Why this matters: run detail is the most sensitive former Jinja screen.

9. Open the old run detail URL.

Page URL: `/admin/agent-tests/ui/runs/run-qa033-failing?tenant_id=11111111-1111-1111-1111-111111111111`

Action: paste the URL into the address bar.

Expected: the browser redirects to React with `run_id=run-qa033-failing` and the
Acme `tenant_id`.

What is happening: the old route checks access before redirecting.

Why this matters: direct run links must not leak unauthorized run existence.

10. Review artifact metadata.

Page URL: `/admin/app/test-bench?artifact_reference_id=artifact-qa033-summary`

Action: inspect artifact label, classification, checksum, redaction summary,
and authorized link.

Expected: no local path, storage path, raw artifact body, or private payload is
visible.

What is happening: React displays only backend-approved artifact metadata.

Why this matters: artifact evidence often points at protected run output.

11. Review unavailable artifact and redaction states.

Page URL: `/admin/app/test-bench?artifact_reference_id=artifact-unavailable-qa043`

Action: inspect the unavailable state.

Expected: the UI shows a clear unavailable status and remediation without
revealing hidden storage details.

What is happening: the backend labels unavailable evidence explicitly.

Why this matters: missing redaction or artifact evidence must block publication
without exposing raw data.

12. Review publish gates.

Page URL: `/admin/app/test-bench?gate_id=gate-qa033-stale`

Action: inspect stale, missing, failed, passed, audit unavailable, and redaction
unavailable gate rows.

Expected: each gate includes target revision, reason, remediation, and audit
reference where available.

What is happening: React renders backend-owned publish-gate evidence.

Why this matters: copied or stale run evidence must not satisfy publication.

13. Refresh gate evidence if enabled.

Page URL: `/admin/app/test-bench?gate_id=gate-qa033-passed`

Action: click the gate refresh action and capture
`output/playwright/qa043_ui/manual-gate-refresh.png`.

Expected: the mutation result shows backend acceptance and a safe audit
reference.

What is happening: the backend recomputes gate evidence for the selected target
revision.

Why this matters: users need recoverability without client-side gate decisions.

14. Review audit timeline.

Page URL: `/admin/app/test-bench?audit_ref=audit-gate-qa033-passed`

Action: inspect audit events and reviewer-safe labels.

Expected: events show actor, action, target, status, and references without raw
request or response bodies.

What is happening: React displays redacted audit summaries.

Why this matters: governance evidence must be inspectable after Jinja removal.

15. Switch to `tenant-admin-acme`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-admin-acme`.

Expected: the browser lands on the tenant-scoped test bench workspace.

What is happening: local login changes the active principal and tenant scope.

Why this matters: tenant administrators should see only authorized Acme data.

16. Check cross-tenant denial.

Page URL: `/admin/agent-tests/ui?tenant_id=22222222-2222-2222-2222-222222222222`

Action: while signed in as `tenant-admin-acme`, paste the URL.

Expected: the browser shows a safe denied state or non-Jinja denial and does not
display Globex private data.

What is happening: the old route validates tenant access before redirecting.

Why this matters: redirects must fail closed.

17. Run a visual redaction scan.

Page URL: `/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111`

Action: search the page text for `raw prompt`, `raw completion`, `memory
contents`, `authorization header`, `resolved credential`, `raw external`,
`storage path`, and `/Users/`.

Expected: none of those strings appear.

What is happening: schemas and builders reject unsafe text before React renders
it.

Why this matters: Jinja removal must not move unsafe content into React.

## Required Automated Evidence

Run the focused UI tests.

```bash
cd frontend/admin
npm test -- --run src/components/testBench src/App.test.tsx
cd ../..
```

Expected: all test bench component tests and app route tests pass.

Run the production React build.

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected: `tsc` and Vite complete, and the React manifest points at the built
asset.

Run the backend route and retirement checks.

```bash
uv run pytest --no-cov tests/integration/api/test_admin_agent_tests_legacy_redirects.py tests/integration/api/test_admin_agent_tests_api.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_test_bench_jinja_retirement.py
```

Expected: all focused backend tests pass.

Run the project quality commands.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all gates pass before release.

Run the Spec 043 UI validator.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: Playwright captures
`output/playwright/qa043_ui/qa043-react-ui2-smoke.png`.

## UI Evidence Checklist

- `manual-test-bench-home.png` shows the React test bench landing page.
- `manual-gate-refresh.png` shows safe gate refresh evidence.
- `qa043-react-ui2-smoke.png` shows the automated React smoke route.
- Notes confirm `/admin/agent-tests/ui` redirects to React.
- Notes confirm `/admin/agent-tests/ui/suites/new` preserves `tenant_id` and
  `mode=create-suite`.
- Notes confirm `/admin/agent-tests/ui/runs/run-qa033-failing` preserves
  `run_id`.
- Notes confirm Acme cannot view Globex tenant data.
- Notes confirm artifact detail is metadata-only.
- Notes confirm no raw prompt, completion, memory, secret, header, raw external
  payload, or local path appears.

## Acceptance Notes Template

```text
Reviewer:
Date:
Browser:
Principal sequence: platform-admin -> tenant-admin-acme
Primary route:
Screenshots:
Legacy redirects checked:
Tenant isolation checked:
Gate refresh checked:
Artifact metadata checked:
Redaction strings checked:
Decision:
Notes:
```

Expected: every note maps to a screenshot, test log, or saved browser
observation.

## Troubleshooting

- If login does not persist, confirm `.env` has
  `LOCAL_PRINCIPAL_COOKIE_NAME=map_local_principal`.
- If the React page is blank, rebuild assets with
  `cd frontend/admin && npm run build`.
- If `/admin/app/test-bench` returns `401`, sign in with local login or send
  `X-Local-Principal`.
- If tenant URLs return `403`, check the `tenant_id` belongs to the selected
  principal.
- If legacy URLs return old HTML, stop and inspect `admin_agent_tests.py`.
- If gate evidence looks current for the wrong target revision, treat it as a
  blocker.
- If artifact detail exposes raw content or storage paths, preserve the
  screenshot and file a blocking defect.
- If redaction markers appear, preserve the screenshot and inspect the backend
  schema validators before continuing.

## Related Files

- `specs/043-test-bench-full-react-parity-and-jinja-removal/qa043.md`
- `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/api/schemas/admin_test_bench.py`
- `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- `frontend/admin/src/components/testBench/TestBenchRunDetail.tsx`
- `frontend/admin/src/components/testBench/TestBenchGatePanel.tsx`
- `tests/integration/api/test_admin_agent_tests_legacy_redirects.py`
- `tests/unit/admin/test_test_bench_jinja_retirement.py`
- `output/playwright/qa043_ui/qa043-react-ui2-smoke.png`
