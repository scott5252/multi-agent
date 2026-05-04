# QA024 UI: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Goal

Validate the browser-visible side of QA024.

This UI walkthrough confirms that the Workflow Registry and publish gate show
required test evidence from the repository-backed Agent Test Bench, and that
reviewers can see safe counts and remediation text without reading database
tables.

The deep data checks live in `qa024.md`; this guide is for reviewers who want a
browser-first path.

## How To Use This Guide

Use two terminal windows.

- Terminal A runs the API server.
- Terminal B prepares the QA database and runs automated evidence commands.

Use one browser window for Acme checks.

Use a second browser window or sign out and back in for Globex checks.

Capture screenshots or reviewer notes under `/tmp/qa024-*` and
`output/playwright/qa024_ui`.

When the guide says to copy a draft id, use the id visible in the page URL.

When the guide says to copy a suite id, use the id shown by the Agent Tests
page or by the JSON detail link if the page exposes one.

## Environment Setup

Run these commands from the repository root.

### Environment Step 1 - Copy The QA Environment

```bash
cp specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/.env.qa024 .env
```

Expected: no output.

What is happening: the app is pointed at local-principal auth, fake `qa024/` secrets, and `multi_agent_platform_qa024`.

Why this matters: browser QA must stay isolated from regular developer data and external services.

### Environment Step 2 - Install Dependencies

```bash
uv sync
```

Expected: dependencies install without an error.

What is happening: Python packages for FastAPI, SQLAlchemy, templates, and tests are installed.

Why this matters: the server-rendered admin UI and migrations need the locked dependency set.

### Environment Step 3 - Start PostgreSQL

```bash
docker compose up -d postgres
```

Expected: Docker reports PostgreSQL is running.

What is happening: local database storage is available.

Why this matters: workflow drafts, revisions, suites, runs, and publish gates all persist to PostgreSQL.

### Environment Step 4 - Reset The QA024 Database

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa024 && createdb -U postgres multi_agent_platform_qa024'
```

Expected: no output or a harmless notice.

What is happening: only the dedicated QA024 database is recreated.

Why this matters: the UI should not include stale drafts or suites from another run.

### Environment Step 5 - Apply Migrations

```bash
uv run alembic upgrade head
```

Expected: Alembic finishes without an error.

What is happening: all admin, workflow, publish gate, and agent test tables are created.

Why this matters: the publish gate cannot evaluate evidence unless the registry and test bench tables exist.

### Environment Step 6 - Seed Tenants

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa024 -v ON_ERROR_STOP=1 <<'SQL'
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

Expected: PostgreSQL reports inserted or updated rows.

What is happening: Acme and Globex tenants are available for local-principal login.

Why this matters: QA024 must check both same-tenant acceptance and cross-tenant denial.

### Environment Step 7 - Create Screenshot Directories

```bash
mkdir -p output/playwright/qa024_ui
```

Expected: no output.

What is happening: the screenshot directory exists.

Why this matters: the UI evidence checklist references this path.

### Environment Step 8 - Start The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the API listens on `http://127.0.0.1:8000`.

What is happening: the server-rendered admin pages are available.

Why this matters: every browser step below uses the local app.

## Browser Walkthrough

### Step 1 - Local Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui
```

Navigation path:

1. Find `Acme Tenant Admin`.
2. Confirm the card key is `tenant-admin-acme`.
3. Click the sign-in button.
4. Confirm the next page is `Workflow Registry`.

Expected: the browser lands on `/admin/workflows/ui`.

What is happening: the browser receives a local-principal session cookie.

Why this matters: QA reviewers can validate tenant behavior without Auth0.

### Step 2 - Workflow Registry Landing Page

Open:

```text
http://127.0.0.1:8000/admin/workflows/ui
```

Actions:

1. Confirm the page title says `Workflow Registry`.
2. Confirm the admin shell navigation is visible.
3. Confirm tenant context is Acme.
4. Create a new tenant workflow draft or open an existing Acme draft from this run.

Expected: the page lists draft controls and safe empty states when no drafts exist.

What is happening: the registry is scoped to the signed-in tenant.

Why this matters: required test evidence must be evaluated in the same tenant scope.

### Step 3 - Create Or Open A Workflow Draft

Actions:

1. Create a draft named `QA024 Required Evidence Draft`.
2. Open the draft editor.
3. Save a simple workflow document.
4. Record the draft id from the editor URL in `/tmp/qa024-reviewer-notes.txt`.

Expected: the editor saves and shows a current revision.

What is happening: saving creates or updates the active draft revision.

Why this matters: required test runs must target the current revision id.

### Step 4 - Create Or Open A Same-Tenant Test Suite

Open:

```text
http://127.0.0.1:8000/admin/agent-tests/ui
```

Actions:

1. Confirm the page shows Agent Test Bench controls.
2. Create a suite for the workflow draft target.
3. Set the target type to workflow draft.
4. Use the draft id from Step 3 as the target id.
5. Use the current draft revision id as the target version.
6. Add a deterministic mock case.

Expected: the suite and case save in Acme scope.

What is happening: the suite can now produce repository evidence for the draft.

Why this matters: QA024 only accepts evidence that is stored in the test bench repository.

### Step 5 - Run The Suite

Actions:

1. Run the suite in `mock_model` mode.
2. Wait for the run detail page or run row to show `passed`.
3. Save a screenshot to `output/playwright/qa024_ui/04-passing-suite.png`.

Expected: the run is passed and diagnostics use safe summaries.

What is happening: a durable run row is stored for the suite, target, and target version.

Why this matters: this is the only evidence that should unlock the publish gate.

### Step 6 - Add The Required Test To The Workflow

Open the draft editor again.

Actions:

1. Add the suite id to the workflow required tests area.
2. Save the draft.
3. If saving creates a new revision, rerun the suite against that new revision.
4. Validate the draft.

Expected: validation succeeds after the suite run matches the latest revision.

What is happening: validation calls the repository-backed required-suite evidence service.

Why this matters: manual status fields are ignored, so only current repository evidence counts.

### Step 7 - Review The Publish Gate

Open the publish gate from the draft page.

Actions:

1. Find the readiness summary.
2. Find `Required Test Evidence`.
3. Confirm counts show one required suite and one passing suite.
4. Confirm missing, failing, and stale counts are zero.
5. Confirm the confirm-publish control is enabled.
6. Save a screenshot to `output/playwright/qa024_ui/07-ready-publish-gate.png`.

Expected: the publish gate is ready and shows safe required-test evidence.

What is happening: the page renders the DB-backed summary returned by workflow validation.

Why this matters: reviewers can understand why publication is allowed without reading database rows.

### Step 8 - Stale Evidence UI Check

Actions:

1. Return to the workflow editor.
2. Make a harmless draft change.
3. Save the draft.
4. Do not rerun the suite.
5. Validate again.
6. Open the publish gate.

Expected: the page shows stale required-test evidence and blocks publish.

What is happening: the old passing run no longer targets the current draft revision.

Why this matters: a stale run must not approve a changed workflow.

### Step 9 - Missing Evidence UI Check

Actions:

1. Edit the required test declaration to reference a same-tenant suite id that has no current run.
2. Save and validate.
3. Open the publish gate.

Expected: the page shows missing evidence and blocks publish.

What is happening: the repository lookup found no acceptable current run.

Why this matters: the system fails closed when evidence is absent.

### Step 10 - Cross-Tenant UI Check

Actions:

1. Sign out or open the local login page again.
2. Sign in as `tenant-admin-globex`.
3. Create a Globex suite named `Globex Private Suite`.
4. Sign back in as `tenant-admin-acme`.
5. Attempt to reference the Globex suite id in the Acme draft.
6. Validate and open the publish gate.

Expected: the page blocks publish and does not show `Globex Private Suite`.

What is happening: Acme cannot read another tenant's suite details.

Why this matters: evidence denial should not become a tenant data leak.

### Step 11 - Manual Status Bypass UI Check

Actions:

1. In the workflow document, set any visible manual latest result status field to `passed`.
2. Remove or stale the actual run evidence.
3. Validate and open the publish gate.

Expected: the page still blocks publish.

What is happening: validation ignores manual result status for required publish evidence.

Why this matters: reviewers are proving that only repository-backed current evidence is trusted.

## Required Automated Evidence

Run focused tests:

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_publish_gate.py \
  tests/unit/admin/test_workflow_builder_references.py \
  tests/unit/admin/test_workflow_registry_service.py \
  tests/integration/api/test_admin_workflow_ui.py
```

Expected: all focused tests pass.

Run Playwright UI automation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/024-automatic-test-bench-evidence-integration-workflow-publish-gates/validation.yml --start-processes
```

Expected: screenshots appear under `output/playwright/qa024_ui`.

Run full quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: lint, formatting, typing, and coverage pass.

## UI Evidence Checklist

- Screenshot of Local Login showing `tenant-admin-acme`.
- Screenshot of Workflow Registry in Acme scope.
- Screenshot of Agent Test Suite with workflow draft target.
- Screenshot of passing same-tenant suite run.
- Screenshot of ready publish gate with Required Test Evidence.
- Screenshot of stale publish gate after a draft revision changes.
- Screenshot of missing evidence gate.
- Screenshot or note confirming Globex suite name is hidden from Acme.
- Note confirming manual `latest_result_status` did not unlock publish.
- Note confirming no raw fixtures, transcripts, or secrets appear.

## Acceptance Notes Template

- Reviewer:
- Date:
- Browser:
- QA database: `multi_agent_platform_qa024`
- Ready gate screenshot:
- Blocked gate screenshot:
- Cross-tenant screenshot:
- Focused tests passed:
- Full quality gates passed:
- Notes:

## Troubleshooting

If the login page does not show local principals, restart the API after copying `.env.qa024`.

If the Agent Tests page is denied, confirm the selected principal has `agent-tests:manage`, `agent-tests:run`, and `agent-tests:read`.

If the publish gate shows stale evidence, rerun the suite after the most recent workflow draft save.

If the publish gate shows missing evidence, confirm the suite id is typed exactly and belongs to Acme.

If the cross-tenant check leaks the Globex suite name, stop and report it as a security regression.

If screenshots are missing, confirm `output/playwright/qa024_ui` exists and port `8000` is available.

## Related Files

- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024.md`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024_user_guide.md`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/testing-instructions.md`
- `src/multi_agent_platform/web_admin/templates/workflows/publish_gate.html`
- `src/multi_agent_platform/web_admin/templates/workflows/components/reference_picker.html`
- `tests/integration/api/test_admin_workflow_ui.py`
