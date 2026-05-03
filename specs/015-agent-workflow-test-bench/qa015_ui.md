# QA015 UI: Agent And Workflow Test Bench

## Goal

Validate Spec 015 through the server-rendered admin browser UI. A reviewer can
start from a clean local environment, sign in with local-principal cards, open
the Agent Tests area, create a suite, add a case, launch safe runs, inspect run
diagnostics, and verify tenant isolation and redaction evidence without using
production credentials.

This walkthrough is browser-first. Terminal commands are limited to setup,
server startup, screenshot automation, diagnostics, and quality evidence.

## How To Use This Guide

Use two terminal windows:

- Terminal A runs the API server.
- Terminal B runs setup and automated evidence commands.

Use one browser window for the primary path. Use another tab for Globex denial
and stale evidence checks if you want to preserve the Acme page state. Record
screenshots under `output/playwright/qa015_ui` or reviewer notes under
`/tmp/qa015-*`.

Values to record:

- `QA015_SUITE_ID`: after creating the suite, copy the UUID after
  `/admin/agent-tests/ui/suites/` in the browser URL.
- `QA015_RUN_ID`: after launching a run, copy the UUID after
  `/admin/agent-tests/ui/runs/` in the browser URL.
- `QA015_TARGET_VERSION`: use `draft-rev-1` for the passing path and
  `draft-rev-2` for stale evidence checks.

When a URL below contains one of those names, replace it with the value from
your run.

## Environment Setup

Run these commands from the repository root.

### Environment Step 1 - Back Up Local Environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
```

Expected: no output.

What is happening: the current local `.env` is preserved.

Why this matters: QA015 can use a dedicated environment without losing local
developer settings.

### Environment Step 2 - Copy The QA Environment

```bash
cp specs/015-agent-workflow-test-bench/.env.qa015 .env
```

Expected: no output.

What is happening: the app is pointed at local-principal auth, fake `qa015/`
secret references, `.data/qa015-artifacts`, and the
`multi_agent_platform_qa015` database.

Why this matters: browser QA should not touch production-like credentials or
the default developer database.

### Environment Step 3 - Confirm Tools

```bash
curl --version | head -1
jq --version
```

Expected: each command prints a version.

What is happening: Terminal B confirms the basic tools used by diagnostics.

Why this matters: the main path is browser-first, but evidence capture still
uses local command-line utilities.

### Environment Step 4 - Remove Old Evidence

```bash
find /tmp -type f \( -name 'qa015-*.json' -o -name 'qa015-*.html' -o -name 'qa015-*.txt' \) -exec rm -f {} +
mkdir -p output/playwright/qa015_ui .data/qa015-artifacts
```

Expected: no output.

What is happening: stale API captures are removed and allowed artifact roots
exist.

Why this matters: evidence from this pass should be easy to review.

### Environment Step 5 - Install Dependencies

```bash
uv sync
```

Expected: command completes without an error.

What is happening: project dependencies are installed from the lockfile.

Why this matters: templates, migrations, and tests need the checked-in runtime.

### Environment Step 6 - Start PostgreSQL

```bash
docker compose up -d postgres
```

Expected: Docker reports PostgreSQL is running.

What is happening: the local database service starts.

Why this matters: the Agent Tests UI persists suites, cases, and runs.

### Environment Step 7 - Reset QA015 Database

```bash
docker compose exec -T postgres sh -c \
  'dropdb -U postgres --if-exists multi_agent_platform_qa015 && createdb -U postgres multi_agent_platform_qa015'
```

Expected: no output, or a harmless notice that the database did not exist.

What is happening: only the dedicated QA015 database is reset.

Why this matters: the browser walkthrough starts from clean state.

### Environment Step 8 - Apply Migrations

```bash
uv run alembic upgrade head
```

Expected: migrations complete without an error.

What is happening: tenant, admin shell, runtime, and agent test bench tables
are created.

Why this matters: browser pages depend on the shared application schema.

### Environment Step 9 - Seed Deterministic Tenants

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa015 -v ON_ERROR_STOP=1 <<'SQL'
INSERT INTO tenants (
  tenant_id, slug, display_name, status, created_at, updated_at
) VALUES
  ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (tenant_id) DO UPDATE SET
  slug = EXCLUDED.slug,
  display_name = EXCLUDED.display_name,
  status = EXCLUDED.status,
  updated_at = CURRENT_TIMESTAMP;
SQL
```

Expected: PostgreSQL reports two inserted or updated tenant rows.

What is happening: Acme and Globex are available for local-principal QA.

Why this matters: the walkthrough validates authorized Acme access and Globex
denial.

### Environment Step 10 - Start The API

Run this in Terminal A and keep it open:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected: the server listens on `http://127.0.0.1:8000`.

What is happening: FastAPI serves the admin shell and Agent Tests UI.

Why this matters: every primary lifecycle action below happens in the browser.

## Browser Walkthrough

### Step 1 - Log In As Acme Tenant Admin

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=11111111-1111-1111-1111-111111111111
```

Navigation:

1. Find the `Acme Tenant Admin` card.
2. Confirm the card shows `tenant-admin-acme`.
3. Click `Sign In`.
4. Confirm the browser redirects to `Agent Tests`.

Expected: the page title is `Agent Tests`, the active tenant is Acme, and the
empty-state message says no suites are visible.

What is happening: the browser stores a local QA cookie for the Acme tenant
admin principal.

Why this matters: suite management requires tenant admin authority.

### Step 2 - Review Empty Suite List

Expected: the page shows `No agent test suites are visible`.

What is happening: the clean QA015 database has no suites for Acme.

Why this matters: the reviewer can prove later rows were created in this pass.

Evidence: capture a screenshot named `qa015-02-empty-agent-tests.png`.

### Step 3 - Open The Create Suite Form

Click `Create Suite`.

Expected: the browser opens `/admin/agent-tests/ui/suites/new`.

What is happening: the server renders a tenant-scoped suite creation form.

Why this matters: non-developer admins can create suites without using the API.

Evidence: confirm fields for Name, Target type, Target id, Target version,
Safe mode, Model mode, Tool mode, Pass threshold, and Required for publish.

### Step 4 - Create The Draft Workflow Guard Suite

Use these form values:

```text
Name: QA015 Draft Workflow Guard
Description: Guard a workflow draft before publication.
Target type: Workflow draft
Target id: qa015-draft-triage
Target version: draft-rev-1
Safe mode: Mock model
Model mode: mock
Tool mode: mock
Pass threshold: 1.0
Required for publish: checked
```

Click `Create Suite`.

Expected: the browser redirects to a suite detail page for
`QA015 Draft Workflow Guard`.

What is happening: the tenant-scoped suite is persisted with a target and
publication gate flag.

Why this matters: publish gates use required suites as release evidence.

Evidence: record `QA015_SUITE_ID` from the URL.

### Step 5 - Review Suite Detail

Expected: the detail page shows target `workflow_draft / qa015-draft-triage /
draft-rev-1`, safe mode `mock_model`, and a redaction notice.

What is happening: the suite detail view renders safe metadata only.

Why this matters: suite pages must not expose raw fixture, prompt, credential,
provider, or transcript content.

Evidence: capture a screenshot named `qa015-05-suite-detail-empty.png`.

### Step 6 - Add A Passing Case

In the `Add Case` form, use:

```json
{"request":"summarize intake","priority":"routine","api_key":"qa015-fake-value"}
```

For expected contract shape, use:

```json
{"status":{},"contract":{}}
```

For assertions, use:

```json
[{"kind":"deterministic","path":"status","comparator":"equals","expected_value":"passed"},{"kind":"deterministic","path":"contract.summary","comparator":"contains","expected_value":"intake"}]
```

Click `Add Case`.

Expected: the suite detail page reloads and shows `Passing intake case` in the
Cases table.

What is happening: fixture data is summarized and assertions are stored.

Why this matters: admins can express expected behavior before running tests.

Evidence: confirm the raw fake value is not visible in the Cases table.

### Step 7 - Run With Mock Model

In the `Run Suite` form, choose:

```text
Safe mode: Mock model
Target version: draft-rev-1
```

Click `Run Tests`.

Expected: the browser redirects to a run detail page with status `passed` and
pass status `passed`.

What is happening: deterministic sandbox output is evaluated against contract
and assertions.

Why this matters: the safest execution path should be deterministic and quick.

Evidence: record `QA015_RUN_ID` from the URL.

### Step 8 - Inspect Run Summary

Expected: the page shows latency, token usage, target version, redaction
summary, artifact summary, and zero or more blocked side effects.

What is happening: the run detail view combines stored run and run-step
metadata.

Why this matters: release reviewers need actionable evidence without raw
runtime payloads.

Evidence: capture a screenshot named `qa015-08-run-summary.png`.

### Step 9 - Inspect Trace Steps

Expected: the Trace Steps table shows the case name, status, model provider,
model id, contract status, assertion outcomes, and side-effect decisions.

What is happening: per-case diagnostics are rendered from durable run-step
records.

Why this matters: admins can see why a suite passed or failed.

Evidence: confirm assertion rows show `passed` and no raw transcript body is
visible.

### Step 10 - Run With Mocked Gateway Mode

Use the browser Back button to return to the suite page. In `Run Suite`, choose:

```text
Safe mode: Real model, side effects disabled
Target version: draft-rev-1
```

Click `Run Tests`.

Expected: the run passes, the model provider is `mocked-gateway`, and the
Trace Steps table shows `external_dependency.write blocked`.

What is happening: the test bench records gateway-style metadata while
blocking tool side effects.

Why this matters: model routing metadata can be reviewed without allowing
unsafe external writes.

Evidence: capture a screenshot named `qa015-10-mocked-gateway-run.png`.

### Step 11 - Check Suite Run List

Return to the suite detail page.

Expected: the Runs table contains at least two rows, one for `mock_model` and
one for `real_model_side_effects_disabled`.

What is happening: prior run results remain visible for the suite.

Why this matters: admins need durable evidence history for a target version.

Evidence: record the latest run statuses.

### Step 12 - Review Publish Gate Status

Expected: the suite detail page shows a publish gate status of ready with
passing evidence after at least one passing current run.

What is happening: the page evaluates required suite evidence for the suite
target and version.

Why this matters: workflow publication can require current passing tests.

Evidence: capture the gate status with the suite target visible.

### Step 13 - Log In As Globex Tenant Admin

Open a new tab:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=22222222-2222-2222-2222-222222222222
```

Click `Globex Tenant Admin`.

Expected: the Agent Tests page shows no Acme suite rows.

What is happening: the active tenant scope changed to Globex.

Why this matters: tenant isolation must hold in the browser UI.

Evidence: capture a screenshot named `qa015-13-globex-empty.png`.

### Step 14 - Attempt Direct Acme Suite Access As Globex

In the Globex tab, open:

```text
http://127.0.0.1:8000/admin/agent-tests/ui/suites/QA015_SUITE_ID
```

Expected: the request is denied and the page does not reveal Acme target names,
case names, fixture values, prompts, transcripts, or artifact paths.

What is happening: route-level tenant checks reject cross-tenant access.

Why this matters: direct links must fail closed, not only navigation links.

Evidence: capture a denial screenshot or note the HTTP status.

### Step 15 - Verify Redaction Language

Return to the Acme run detail page and review the redaction notice.

Expected: the page states that fixtures, prompts, provider messages,
credentials, tool payloads, and transcripts are redacted.

What is happening: every visible evidence page reminds reviewers that inline
content is safe summary data.

Why this matters: manual reviewers need a clear signal when evidence is
intentionally summarized.

Evidence: search the page for `qa015-fake-value`; it should not appear.

## Required Automated Evidence

Run the Playwright validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml --start-processes
```

Expected: screenshots are written under `output/playwright/qa015_ui`.

What is happening: the validation runner opens the local login page and the
Agent Tests target page.

Why this matters: automated browser evidence protects the basic UI entry path.

Run QA docs validation:

```bash
.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/015-agent-workflow-test-bench
```

Expected: QA document validation passes.

What is happening: the docs validator checks this UI guide, `qa015.md`, and
`.env.qa015`.

Why this matters: reviewers get complete, repeatable instructions.

Run focused UI and API tests:

```bash
uv run pytest --no-cov tests/integration/api/test_admin_agent_tests_api.py
```

Expected: UI route rendering and API lifecycle tests pass.

What is happening: FastAPI test clients exercise the suite create, case add,
run launch, run detail, publish gate, and tenant denial surfaces.

Why this matters: browser behavior remains covered in automated tests.

Run repository quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: each command passes.

What is happening: linting, formatting, typing, and coverage all validate the
implementation.

Why this matters: QA015 should not lower the repository quality bar.

## UI Evidence Checklist

- Local login screenshot shows Acme and Globex local-principal cards.
- Empty Agent Tests page shows no suites for a clean Acme database.
- Create Suite form shows target, safe mode, model mode, tool mode, threshold,
  and required-for-publish controls.
- Suite detail shows target, safe mode, publish gate status, add case form,
  cases table, and runs table.
- Case table shows safe fixture metadata and assertion summaries.
- Mock-model run detail shows pass status, latency, token usage, contract
  status, and assertion outcomes.
- Mocked-gateway run detail shows provider metadata and blocked side effects.
- Redaction notice appears on suite and run detail pages.
- Globex suite list does not show Acme suite data.
- Direct Globex access to Acme suite is denied without protected details.
- Screenshots are saved under `output/playwright/qa015_ui`.
- Notes and JSON evidence are saved under `/tmp/qa015-*`.

## Acceptance Notes Template

Use this template for manual review notes:

- Reviewer:
- Date:
- Branch:
- Environment file: `specs/015-agent-workflow-test-bench/.env.qa015`
- Acme login result:
- Suite id:
- Case creation result:
- Mock-model run id:
- Mocked-gateway run id:
- Publish gate status:
- Globex isolation result:
- Redaction scan result:
- Playwright output directory:
- QA docs validation result:
- Ruff result:
- Format result:
- mypy result:
- Coverage result:
- Expected limitations:
- Regressions:

## Troubleshooting

- If the login page is missing, restart the API after copying `.env.qa015`.
- If the Acme card is missing, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.
- If the suite create form says tenant id is required, open the UI with
  `tenant_id=11111111-1111-1111-1111-111111111111`.
- If the Cases table does not update, verify the fixture and assertion text is
  valid JSON.
- If a run fails unexpectedly, open Trace Steps and inspect contract and
  assertion diagnostics.
- If mocked-gateway mode does not show blocked side effects, confirm the safe
  mode was `real_model_side_effects_disabled`.
- If Globex can see Acme data, stop validation and inspect tenant checks.
- If raw fake fixture values appear on the page, stop validation and inspect
  redaction helpers before continuing.
- If Playwright fails to start processes, inspect `/tmp/qa015-api.log` and
  `/tmp/qa015-worker.log`.
- If screenshots are blank, confirm the base URL is
  `http://127.0.0.1:8000` and the API is still running.

## Related Files

- `specs/015-agent-workflow-test-bench/qa015.md`
- `specs/015-agent-workflow-test-bench/qa015_user_guide.md`
- `specs/015-agent-workflow-test-bench/.env.qa015`
- `src/multi_agent_platform/web_admin/templates/agent_tests/index.html`
- `src/multi_agent_platform/web_admin/templates/agent_tests/suite_form.html`
- `src/multi_agent_platform/web_admin/templates/agent_tests/suite_detail.html`
- `src/multi_agent_platform/web_admin/templates/agent_tests/run_detail.html`
- `tests/integration/api/test_admin_agent_tests_api.py`
