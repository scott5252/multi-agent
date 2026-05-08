# QA052 UI Walkthrough: Skill Lifecycle React Live Data

## Goal

Guide a reviewer through browser evidence for qa052.

Expected: the React skill lifecycle workspace loads from live backend records.

Expected: the browser shows the seeded `qa052-calendar-assistant` package only
after the QA seed command persists it.

Expected: the reviewer can click `Save reference` and see a successful mutation
result in the browser.

Expected: the post-UI verifier proves the credential readiness row changed from
pending to ready.

Why this matters: qa052 removes fixed skill lifecycle rows from production code,
so the browser must prove it can operate from durable backend state.

## How To Use This Guide

Use this walkthrough together with `qa052.md`.

Save screenshots under `output/playwright/qa052_ui` or `/tmp/qa052-*`.

Use `/tmp/qa052-ui-post-api-notes.txt` for written reviewer notes.

Expected: screenshot filenames include qa052.

Expected: reviewer notes mention the login principal and action result.

Expected: the browser evidence matches API evidence from `qa052.md`.

What is happening: the browser signs in with a local principal and uses the
same FastAPI routes as automated Playwright.

Why this matters: browser evidence should not rely on hidden test fixtures.

## Environment Setup

Copy the environment.

```bash
cp specs/052-skill-lifecycle-react-live-data/.env.qa052 .env
uv sync
```

Expected: `.env.qa052` is active and dependencies are installed.

Reset and migrate the database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa052 && createdb -U postgres multi_agent_platform_qa052'
uv run alembic upgrade head
```

Expected: only `multi_agent_platform_qa052` is recreated.

Seed local tenants and skill rows.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa052 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
uv run python scripts/qa/seed_skill_lifecycle_qa052.py
```

Expected: the seed command prints `Seeded QA052 skill lifecycle records`.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the API is reachable at `http://127.0.0.1:8000`.

What is happening: the app is configured for local-principal qa052 review.

Why this matters: the browser and database must use the same isolated
environment.

## Browser Walkthrough

Step 1: Open the login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Expected: the local login page lists `tenant-admin-acme`.

What is happening: local-principal auth is used instead of Auth0.

Why this matters: the reviewer uses deterministic local roles with no external
identity dependency.

Step 2: Choose `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app/skills`.

Expected: the page heading says `Skill lifecycle`.

Reviewer evidence: save `/tmp/qa052-ui-login.png`.

Step 3: Review the seeded skill lifecycle state.

Expected: the page shows `qa052-calendar-assistant`.

Expected: the page shows `QA052 Calendar OAuth reference`.

Expected: the page shows a provenance source named `Skill lifecycle records`.

Expected: the page does not show raw manifests or credential values.

What is happening: React renders package, grant, installation, connector,
diagnostic, binding, and audit panels from live API responses.

Why this matters: seeded data came from the QA seed script, not production
builders.

Step 4: Save the credential reference.

Click `Save reference`.

Expected: a result card appears with `accepted`.

Expected: the result summary says `Credential reference configured without
exposing values.`

Expected: no resolved credential value appears on screen.

Reviewer evidence: save `/tmp/qa052-ui-credential-save.png`.

Step 5: Verify persistence.

```bash
uv run python scripts/qa/verify_skill_lifecycle_qa052.py
```

Expected: the verifier prints `Verified QA052 skill lifecycle credential
persistence`.

Expected: the verifier prints `credential_status=ready`.

Reviewer evidence: copy output to `/tmp/qa052-ui-post-api-notes.txt`.

Step 6: Verify tenant isolation.

Open this URL after signing in as `tenant-admin-globex`.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: Globex sees a skill lifecycle empty state.

Expected: Globex does not see `qa052-calendar-assistant`.

Reviewer evidence: save `/tmp/qa052-ui-globex-empty.png`.

What is happening: the active tenant scope changes and the backend filters
skill rows by tenant.

Why this matters: tenant isolation must survive the live-data migration.

## Required Automated Evidence

Run the generated contract check.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: generated contracts are current.

Run backend and frontend checks.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_skill_lifecycle_schema.py tests/unit/admin/test_skill_lifecycle_service.py tests/performance/skills/test_skill_lifecycle_queries.py tests/unit/admin/test_live_data_inventory_scanner.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py -q
npm run --prefix frontend/admin test -- --run src/components/skills
npm run --prefix frontend/admin typecheck
npm run --prefix frontend/admin build
```

Expected: focused backend and frontend checks pass.

Run project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: project quality gates pass.

Run Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml --start-processes
```

Expected: Playwright captures `output/playwright/qa052_ui/qa052-live-data-ui-api-smoke.png`.

What is happening: Playwright repeats the tenant login and credential-save path.

Why this matters: the automated UI check proves the reviewer path is repeatable.

## UI Evidence Checklist

- `/tmp/qa052-ui-login.png`
- `/tmp/qa052-ui-credential-save.png`
- `/tmp/qa052-ui-globex-empty.png`
- `/tmp/qa052-ui-post-api-notes.txt`
- `output/playwright/qa052_ui/qa052-live-data-ui-api-smoke.png`

Expected: screenshots show only safe summaries and identifiers.

Expected: reviewer notes include the verifier output.

Expected: evidence mentions the `tenant-admin-acme` principal.

Expected: evidence mentions the Globex empty-state check.

What is happening: reviewers collect both visual and backend proof.

Why this matters: visual confirmation alone is not enough for qa052 completion.

## Redaction Checks

Review the browser and captured evidence for unsafe text.

```bash
grep -RniE 'raw manifest|resolved credential|authorization header|connector payload|raw tool output|/Users/' /tmp/qa052-* output/playwright/qa052_ui || true
```

Expected: no protected content appears.

Expected: credential evidence appears only as ids or fingerprints.

Expected: local absolute paths are absent.

What is happening: the UI uses safe summaries returned by backend contracts.

Why this matters: skill lifecycle screens touch credential and connector
surfaces, so redaction boundaries are high risk.

## Acceptance Notes Template

Use this template in `/tmp/qa052-ui-post-api-notes.txt`.

```text
qa052 browser login principal:
qa052 seeded package visible:
qa052 credential save result:
qa052 post-UI database verification:
qa052 Globex empty state:
qa052 Playwright screenshot:
qa052 redaction notes:
```

Expected: every line contains a concrete result.

Expected: no line contains a secret, credential value, raw manifest, or local
absolute path.

What is happening: the reviewer records a compact audit trail.

Why this matters: qa052 status history should cite reproducible evidence.

## Troubleshooting

If the browser shows a generic unavailable page, confirm the API is running.

If the page does not show `qa052-calendar-assistant`, rerun
`uv run python scripts/qa/seed_skill_lifecycle_qa052.py`.

If `Save reference` is missing, confirm you signed in as `tenant-admin-acme`.

If the verifier still sees `pending`, rerun the browser save action and refresh.

If Globex sees Acme package data, stop and treat it as a blocker.

If Playwright cannot click the local-login form, verify `.env.qa052` was copied
and `LOCAL_PRINCIPAL_CATALOG_JSON` contains `tenant-admin-acme`.

Expected: troubleshooting stays inside qa052 database and local-principal mode.

Expected: no live provider, Telegram, external connector, or production
credential call is made.

What is happening: each failure mode isolates either environment, seed,
authorization, UI action, or persistence.

Why this matters: qa052 must not be marked complete from partial visual
evidence.

## Related Files

- `specs/052-skill-lifecycle-react-live-data/qa052.md`
- `specs/052-skill-lifecycle-react-live-data/qa052_user_guide.md`
- `specs/052-skill-lifecycle-react-live-data/.env.qa052`
- `scripts/qa/seed_skill_lifecycle_qa052.py`
- `scripts/qa/verify_skill_lifecycle_qa052.py`
- `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- `src/multi_agent_platform/admin/skill_lifecycle.py`

Expected: these files explain the qa052 browser flow and verification evidence.

Why this matters: the walkthrough can be repeated by a reviewer after this
autopilot run.
