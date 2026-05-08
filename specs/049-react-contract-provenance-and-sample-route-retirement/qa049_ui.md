# QA049 UI: React Contract Provenance And Sample Route Retirement

## Goal

Guide a reviewer through browser evidence for qa049.

The UI review confirms that the React admin shell still loads, the migration workspace renders live-data guardrail information, command search does not expose the retired sample route, and `/admin/app/patterns` no longer renders sample pattern data.

## How To Use This Guide

Run the setup commands from the repository root.

Use a browser pointed at `http://127.0.0.1:8000/auth/local-login`.

Save screenshots and notes under these names:

- `/tmp/qa049-ui-login.png`
- `/tmp/qa049-ui-admin-home.png`
- `/tmp/qa049-ui-migration.png`
- `/tmp/qa049-ui-patterns-retired.png`
- `/tmp/qa049-ui-search-notes.txt`

Expected: every screenshot or note file references qa049 and avoids raw secrets, private messages, raw prompt text, memory contents, provider payloads, and local absolute paths.

What is happening: the reviewer is collecting visual and route evidence that matches the backend API checks.

Why this matters: qa049 is a contract and route-retirement spec, so the browser must prove the user-facing shell did not keep a hidden sample route alive.

## Environment Setup

### 1. Copy the QA environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049 .env
uv sync
```

Expected: `.env.qa049` is active and dependencies are available.

What is happening: the app is configured for local-principal qa049 review.

Why this matters: the browser must use deterministic local principals and the `multi_agent_platform_qa049` database.

### 2. Prepare the QA database

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa049 && createdb -U postgres multi_agent_platform_qa049'
uv run alembic upgrade head
```

Expected: migrations complete without errors.

What is happening: the React admin shell will read tenant and route metadata from the QA database.

Why this matters: the UI review must not depend on a developer's existing local data.

### 3. Seed tenants

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa049 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Expected: Acme and Globex tenants exist.

What is happening: local login will be able to select platform and tenant principals.

Why this matters: route retirement must hold for platform and tenant-shaped access.

### 4. Build the React assets

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected: the build writes `src/multi_agent_platform/web_admin/static/react/manifest.json`.

What is happening: FastAPI will serve the updated React bundle.

Why this matters: the retired route cannot be tested against stale assets.

### 5. Start the app

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the app starts at `http://127.0.0.1:8000`.

What is happening: the browser will use the same app instance as the API evidence.

Why this matters: qa049 acceptance needs matching browser and backend behavior.

## Browser Walkthrough

### 1. Local login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Select `platform-admin`.

Expected: the browser lands on `/admin/app` and shows the React admin shell.

What is happening: local-principal auth sets the safe reviewer identity.

Why this matters: the retired patterns route must be unavailable to a powerful principal, not only to low-privilege users.

Reviewer evidence: save `/tmp/qa049-ui-login.png`.

### 2. Admin home shell

Open:

```text
http://127.0.0.1:8000/admin/app
```

Review the left navigation, breadcrumbs, page actions, and shell state area.

Expected: navigation does not include `Forms and data patterns` or `/admin/app/patterns`.

What is happening: the shell is built from backend authorized navigation.

Why this matters: sample routes must not remain discoverable through navigation.

Reviewer evidence: save `/tmp/qa049-ui-admin-home.png`.

### 3. Migration workspace

Open:

```text
http://127.0.0.1:8000/admin/app/migration
```

Find the live-data guardrails or live-data inventory panel.

Expected: the migration workspace renders scanner status, route targets, evidence references, and safe state copy without raw payloads.

What is happening: the UI is reading the backend migration JSON contracts.

Why this matters: qa049 relies on Spec 048 scanner evidence to prevent new mock-data regressions.

Reviewer evidence: save `/tmp/qa049-ui-migration.png`.

### 4. Command search omission

Use the command or search control in the shell and search for `patterns`.

Expected: no search result opens `/admin/app/patterns`.

What is happening: the client displays backend command results derived from authorized navigation.

Why this matters: retiring a route also requires removing indirect UI entry points.

Reviewer evidence: write the observed result list to `/tmp/qa049-ui-search-notes.txt`.

### 5. Retired sample route

Open:

```text
http://127.0.0.1:8000/admin/app/patterns
```

Expected: the page does not show sample records, sample forms, sample exports, or the old patterns page. A 404 or safe unavailable response is acceptable.

What is happening: the production sample route has been removed from the React host fallback.

Why this matters: the page must not silently satisfy validation with fake sample data.

Reviewer evidence: save `/tmp/qa049-ui-patterns-retired.png`.

### 6. Retired sample JSON

Run from a terminal while the browser session is active:

```bash
curl -sS -o /tmp/qa049-ui-patterns-json.txt -w 'HTTP_STATUS=%{http_code}\n' -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/patterns.json'
```

Expected: the terminal prints `HTTP_STATUS=404`.

What is happening: the JSON route is unavailable even for the platform reviewer.

Why this matters: the browser cannot be backed by a hidden sample JSON envelope.

### 7. Retired sample action

Run:

```bash
curl -sS -o /tmp/qa049-ui-patterns-action.txt -w 'HTTP_STATUS=%{http_code}\n' -X POST -H 'Content-Type: application/json' -H 'X-Local-Principal: platform-admin' -d '{"sample_name":"Preview"}' 'http://127.0.0.1:8000/admin/app/patterns/actions/sample'
```

Expected: the terminal prints `HTTP_STATUS=404` or `HTTP_STATUS=405`.

What is happening: the sample action cannot produce a mutation result.

Why this matters: fake mutation success must not remain reachable through a retired UI path.

### 8. Retired sample export

Run:

```bash
curl -sS -o /tmp/qa049-ui-patterns-export.txt -w 'HTTP_STATUS=%{http_code}\n' -X POST -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/patterns/export'
```

Expected: the terminal prints `HTTP_STATUS=404` or `HTTP_STATUS=405`.

What is happening: the sample export route cannot return fake artifact references.

Why this matters: reviewers must not mistake sample export snapshots for real persisted artifacts.

### 9. Tenant admin smoke check

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app?tenant_id=11111111-1111-1111-1111-111111111111
```

Select `tenant-admin-acme`.

Expected: the shell loads with Acme scope and still omits `/admin/app/patterns`.

What is happening: tenant-scoped navigation is rebuilt for the tenant admin.

Why this matters: route retirement must hold across supported auth shapes.

### 10. Cross-tenant negative check

Run:

```bash
curl -sS -o /tmp/qa049-ui-cross-tenant.txt -w 'HTTP_STATUS=%{http_code}\n' -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/app/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222'
```

Expected: the terminal prints `HTTP_STATUS=403`.

What is happening: Acme cannot bootstrap Globex scope.

Why this matters: the route cleanup must not weaken tenant isolation.

### 11. Redaction spot check

Run:

```bash
grep -RInE 'sk-|authorization:|bearer |raw prompt|raw completion|memory contents|provider payload|tool payload|/Users/' /tmp/qa049-ui-* || true
```

Expected: no evidence file contains raw secrets, raw prompts, memory contents, provider payloads, tool payloads, or local absolute paths.

What is happening: reviewer artifacts are scanned before acceptance.

Why this matters: qa049 adds visible metadata and must keep that metadata safe.

## Required Automated Evidence

Run the focused browser and frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm test -- --run
npm run build
```

Expected: all frontend checks pass.

What is happening: the React app, router tests, metadata helper tests, and build are validated together.

Why this matters: the UI cannot rely on old generated contracts or stale sample components.

Run backend checks:

```bash
uv run pytest --no-cov tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py -q
```

Expected: focused backend checks pass.

What is happening: schema, OpenAPI, route, and scanner expectations are executed.

Why this matters: the UI proof needs matching backend proof.

Run project quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: quality gates pass or a reviewer records the exact blocker.

What is happening: qa049 is checked against the project-wide release bar.

Why this matters: a route cleanup touching shared contracts needs broad safety evidence.

Run the automated UI validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml --start-processes
```

Expected: Playwright captures `output/playwright/qa049_ui/qa049-live-data-ui-api-smoke.png`.

What is happening: the autopilot reproduces the browser smoke flow.

Why this matters: screenshots and automated navigation guard against accidental blank shells.

## UI Evidence Checklist

- Expected: `/admin/app` loads after local login.
- Expected: shell navigation omits `/admin/app/patterns`.
- Expected: command search omits `/admin/app/patterns`.
- Expected: `/admin/app/migration` renders live-data guardrail evidence.
- Expected: `/admin/app/patterns` does not show sample records or sample forms.
- Expected: `/admin/app/patterns.json` returns 404.
- Expected: sample action and export routes return 404 or 405.
- Expected: tenant-admin Acme cannot access Globex bootstrap.
- Expected: screenshots and notes contain no unsafe raw values.

## Acceptance Notes Template

```text
qa049 UI reviewer:
date:
browser:
principal reviewed:
admin home screenshot:
migration screenshot:
patterns retired screenshot:
search omission notes:
retired route status:
redaction scan:
known limitations:
decision:
```

Expected: every line is filled with a concrete file path, status, or reviewer note.

What is happening: the reviewer records repeatable evidence instead of relying on memory.

Why this matters: qa049 changes are subtle and need crisp acceptance notes.

## Troubleshooting

- If the login page does not list `platform-admin`, recopy `.env.qa049` and restart the API.
- If the browser opens an old bundle, rerun `npm run build` in `frontend/admin`.
- If `/admin/app/patterns` renders a page, verify `frontend/admin/src/App.tsx` and `src/multi_agent_platform/api/routers/admin_react.py`.
- If search returns the patterns route, rerun the bootstrap and search API checks.
- If Playwright fails to start processes, stop any existing server on port 8000.
- If a screenshot contains raw internal paths, retake it after closing developer tooling.
- If a POST route returns 405, record it as acceptable for the retired sample action or export path.

## Related Files

- `specs/049-react-contract-provenance-and-sample-route-retirement/qa049.md`
- `specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/routes.tsx`
- `frontend/admin/src/utils/adminActionMetadata.ts`
- `frontend/admin/src/components/states/CommonState.tsx`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `tests/integration/test_admin_react_routes.py`
- `output/playwright/qa049_ui`
