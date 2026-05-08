# QA052 User Guide: Spec 052 - Skill Lifecycle React Live Data

## Detailed Overview

QA052 verifies the Skill Lifecycle workspace in the React admin app.

The workspace helps authorized admins review skill packages, tenant grants,
tenant installations, credential readiness, smoke-test evidence, connector
diagnostics, binding previews, and lifecycle audit records.

Before this spec, the React skill lifecycle page could show deterministic
production rows that looked like real skill data.

This spec changes that behavior.

The page must now show live records from the database or a clear empty state.

The browser action for this QA run is saving a credential reference.

That action is safe because it stores credential reference metadata only.

It never resolves or displays a credential value.

It never calls a live provider.

It never calls Telegram.

It never calls an external connector.

It never displays raw manifests, connector payloads, raw tool output, or local
file paths.

The seeded package for the QA run is `qa052-calendar-assistant`.

The seeded Acme tenant can see and update it.

The Globex tenant must not see Acme skill rows.

The expected browser result is a successful credential-save message.

The expected database result is a ready credential row and a ready installation
credential status.

## Who Should Use This Guide

Use this guide if you are manually reviewing qa052.

Use it if you need to confirm the browser behavior after automated tests pass.

Use it if you need to collect screenshots for a reviewer.

Use it if you need to verify redaction and tenant isolation.

You do not need to know the code internals to follow this guide.

You do need terminal access to the repository.

You do need Docker/PostgreSQL available locally.

You do need the local app to run against `.env.qa052`.

## Manual QA Prerequisites

Confirm you are in the repository root.

```bash
pwd
```

Expected result: the path ends in `multi-agent`.

Copy the QA environment.

```bash
cp specs/052-skill-lifecycle-react-live-data/.env.qa052 .env
```

Expected result: `.env` now contains `APP_NAME=multi-agent-platform-qa052`.

Install dependencies.

```bash
uv sync
```

Expected result: dependency installation completes.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: the `postgres` service is running.

Reset only the qa052 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa052 && createdb -U postgres multi_agent_platform_qa052'
```

Expected result: the qa052 database is recreated.

Apply migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations complete without errors.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa052 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected result: Acme and Globex are available for local-principal login.

Seed the skill lifecycle records.

```bash
uv run python scripts/qa/seed_skill_lifecycle_qa052.py
```

Expected result: the command prints `Seeded QA052 skill lifecycle records`.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the app is reachable at `http://127.0.0.1:8000`.

## Step-by-Step Manual QA

Step 1: Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Expected result: the local-principal login page opens.

Step 2: Choose `tenant-admin-acme`.

Expected result: the browser opens the Skill Lifecycle page.

Step 3: Confirm the page title.

Expected result: the page shows `Skill lifecycle`.

Step 4: Confirm the seeded package appears.

Expected result: the page shows `qa052-calendar-assistant`.

Step 5: Confirm the credential option appears.

Expected result: the page shows `QA052 Calendar OAuth reference`.

Step 6: Confirm the provenance message.

Expected result: the page shows data from `Skill lifecycle records`.

Step 7: Confirm the page is safe.

Expected result: the page does not show raw manifests, credential values,
authorization headers, connector payloads, raw tool outputs, stack traces, or
local filesystem paths.

Step 8: Click `Save reference`.

Expected result: a mutation result appears with status `accepted`.

Step 9: Read the result message.

Expected result: the result says `Credential reference configured without
exposing values.`

Step 10: Save a screenshot.

Expected result: the screenshot is named `/tmp/qa052-ui-credential-save.png`.

Step 11: Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_skill_lifecycle_qa052.py
```

Expected result: the verifier prints `Verified QA052 skill lifecycle credential
persistence`.

Step 12: Copy verifier output.

Expected result: output is copied to `/tmp/qa052-ui-post-api-notes.txt`.

Step 13: Open the login page again.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: the login page opens.

Step 14: Choose `tenant-admin-globex`.

Expected result: Globex reaches the Skill Lifecycle page.

Step 15: Confirm Globex isolation.

Expected result: Globex sees an empty skill lifecycle state.

Step 16: Confirm Acme data is absent.

Expected result: Globex does not see `qa052-calendar-assistant`.

Step 17: Save a Globex screenshot.

Expected result: the screenshot is named `/tmp/qa052-ui-globex-empty.png`.

Step 18: Record the final manual result.

Expected result: `/tmp/qa052-ui-post-api-notes.txt` includes the Acme action,
database verification, Globex empty state, and redaction notes.

## Expected Results

Expected result: Acme sees the seeded package.

Expected result: Acme sees the seeded installation.

Expected result: Acme can save the credential reference.

Expected result: the credential result does not display a credential value.

Expected result: the post-UI verifier sees `credential_status=ready`.

Expected result: Globex sees an empty state.

Expected result: Globex does not see Acme package data.

Expected result: Playwright captures the same flow.

Expected result: generated TypeScript contracts are current.

Expected result: backend tests pass.

Expected result: frontend tests and build pass.

Expected result: full project quality gates pass.

Expected result: curl regression validation passes.

## Evidence To Capture

Capture `/tmp/qa052-ui-login.png`.

Capture `/tmp/qa052-ui-credential-save.png`.

Capture `/tmp/qa052-ui-globex-empty.png`.

Capture `/tmp/qa052-ui-post-api-notes.txt`.

Capture `output/playwright/qa052_ui/qa052-live-data-ui-api-smoke.png`.

Capture `.data/curl_test_runs/qa052-after-spec`.

Use this notes template.

```text
qa052 login principal:
qa052 seeded package visible:
qa052 credential save result:
qa052 verifier output:
qa052 Globex empty state:
qa052 redaction notes:
qa052 automated validation:
```

Expected result: every evidence item has a concrete file path or command
result.

## Security And Redaction Checks

Search evidence for protected content.

```bash
grep -RniE 'raw manifest|resolved credential|authorization header|connector payload|raw tool output|/Users/' /tmp/qa052-* output/playwright/qa052_ui || true
```

Expected result: no protected content appears.

Expected result: credential evidence appears only as a reference id or
fingerprint.

Expected result: no local absolute path appears in the UI.

Expected result: no raw connector or tool output appears.

## Tenant Isolation Checks

Use Acme for the credential-save action.

Use Globex for the empty-state check.

Expected result: Acme sees `qa052-calendar-assistant`.

Expected result: Globex does not see `qa052-calendar-assistant`.

Expected result: cross-tenant API requests return denied or empty safe states.

Expected result: no Globex response includes Acme-only audit references.

## Automated Validation Commands

Run QA document validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/052-skill-lifecycle-react-live-data
```

Run generated contract validation.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Run backend tests.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_skill_lifecycle_schema.py tests/unit/admin/test_skill_lifecycle_service.py tests/performance/skills/test_skill_lifecycle_queries.py tests/unit/admin/test_live_data_inventory_scanner.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py -q
```

Run frontend checks.

```bash
npm run --prefix frontend/admin test -- --run src/components/skills
npm run --prefix frontend/admin typecheck
npm run --prefix frontend/admin build
```

Run project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run Spec QA and Playwright.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml --start-processes
```

Expected result: all commands pass.

## Troubleshooting

If the package is missing, rerun the seed script.

If the credential save button is missing, confirm you are signed in as
`tenant-admin-acme`.

If the verifier still reports pending, repeat the credential save action.

If the page shows an unavailable state, confirm the API is running.

If the app uses the wrong database, copy `.env.qa052` again.

If Globex sees Acme data, stop and report a tenant isolation blocker.

If protected content appears, stop and report a redaction blocker.

If Playwright fails before login, check the local principal catalog.

If Playwright fails after login, check `/tmp/qa052-api.log`.

If curl validation fails, inspect `.data/curl_test_runs/qa052-after-spec`.

Expected result: troubleshooting stays inside the qa052 database and local QA
environment.
