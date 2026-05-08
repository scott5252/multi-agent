# QA049 User Guide: Spec 049 - React Contract Provenance And Sample Route Retirement

## Detailed Overview

QA049 removes the production sample patterns page from the React admin surface.

The removed page lived at `/admin/app/patterns`.

That page was useful while the React admin primitives were being built.

It is no longer acceptable as a production-like route because it returned sample records, sample form defaults, sample mutation results, and sample export references.

QA049 also adds shared metadata to React admin contracts.

That metadata explains where page state comes from.

It tells reviewers whether a state is live repository data, computed metadata, an empty live state, denied access, or an unavailable dependency.

It also lets admin actions describe whether revisions, idempotency keys, and request identifiers come from the backend or from generated client state.

The reviewer goal is not to test every admin feature.

The reviewer goal is to prove the shell remains usable and the retired sample route cannot return sample data.

The reviewer should also prove the UI and API expose truthful empty-state and provenance information.

The React admin shell should remain the first screen for platform administrators.

The migration workspace should continue to show live-data guardrail evidence.

The command search and navigation should not advertise the retired patterns route.

If `/admin/app/patterns` is opened directly, it should be unavailable.

If `/admin/app/patterns.json` is requested, it should return 404.

If the old sample action or export endpoint is posted to, it should return 404 or 405.

The 405 response is acceptable for old POST routes because the SPA fallback only supports GET.

No reviewer should see sample records named as production data.

No reviewer should see fake sample export snapshots.

No reviewer should see fixed QA idempotency keys in production React source.

No reviewer evidence should contain raw credentials, raw prompts, memory contents, private messages, provider payloads, tool payloads, or local absolute paths.

## Who Should Use This Guide

Use this guide if you are reviewing qa049 manually.

Use this guide if you need a plain-language checklist for browser behavior.

Use this guide if you need to confirm that `/admin/app/patterns` is retired.

Use this guide if you are not planning to inspect code directly.

Use `qa049.md` when you need deeper API, test, and command evidence.

Use `qa049_ui.md` when you need a browser-first walkthrough with screenshot names.

Use this user guide as the short reviewer operating procedure.

## Manual QA Prerequisites

You need a local checkout of the repository.

You need Docker available for PostgreSQL.

You need Node dependencies available for the React admin build.

You need Python dependencies available through `uv`.

You need the qa049 environment file.

The environment file is `specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049`.

The QA database is `multi_agent_platform_qa049`.

The QA storage root is `.data/qa049-artifacts`.

The local browser base URL is `http://127.0.0.1:8000`.

The local login URL is `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`.

The first principal to use is `platform-admin`.

The tenant principal for Acme checks is `tenant-admin-acme`.

The cross-tenant principal for negative checks is `tenant-admin-globex`.

Before starting, close any server already listening on port 8000.

Before starting, save or move any unrelated `.env` file if you need it later.

## Step-by-Step Manual QA

1. Copy the environment file.

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049 .env
```

Expected result: `.env` contains qa049 settings.

2. Install dependencies.

```bash
uv sync
```

Expected result: dependencies install without requiring live external services.

3. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: the PostgreSQL container is running.

4. Reset the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa049 && createdb -U postgres multi_agent_platform_qa049'
```

Expected result: the qa049 database is recreated.

5. Run migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations complete cleanly.

6. Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa049 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Expected result: the seed command succeeds even if tenants already exist.

7. Build the React admin.

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected result: the React asset manifest is updated.

8. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the API is available at `http://127.0.0.1:8000`.

9. Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Expected result: the local login page lists `platform-admin`.

10. Select `platform-admin`.

Expected result: the React admin shell opens.

11. Review the shell navigation.

Expected result: no item points to `/admin/app/patterns`.

12. Open the migration workspace.

```text
http://127.0.0.1:8000/admin/app/migration
```

Expected result: the migration workspace renders live-data guardrail evidence.

13. Use search for `patterns`.

Expected result: no search result points to `/admin/app/patterns`.

14. Open the retired route.

```text
http://127.0.0.1:8000/admin/app/patterns
```

Expected result: the page is unavailable and does not show sample records or sample forms.

15. Check the retired JSON route.

```bash
curl -sS -o /tmp/qa049-user-patterns-json.txt -w 'HTTP_STATUS=%{http_code}\n' -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/patterns.json'
```

Expected result: the status is 404.

16. Check the retired action route.

```bash
curl -sS -o /tmp/qa049-user-patterns-action.txt -w 'HTTP_STATUS=%{http_code}\n' -X POST -H 'Content-Type: application/json' -H 'X-Local-Principal: platform-admin' -d '{"sample_name":"Preview"}' 'http://127.0.0.1:8000/admin/app/patterns/actions/sample'
```

Expected result: the status is 404 or 405.

17. Check the retired export route.

```bash
curl -sS -o /tmp/qa049-user-patterns-export.txt -w 'HTTP_STATUS=%{http_code}\n' -X POST -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/patterns/export'
```

Expected result: the status is 404 or 405.

18. Check bootstrap metadata.

```bash
curl -sS -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/bootstrap.json' | tee /tmp/qa049-user-bootstrap.json | jq '.shell.states[] | select(.state=="empty")'
```

Expected result: the empty state includes provenance and empty-state metadata.

19. Check Acme tenant scope.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected result: `tenant-admin-acme` can open the shell for Acme.

20. Check cross-tenant denial.

```bash
curl -sS -o /tmp/qa049-user-cross-tenant.txt -w 'HTTP_STATUS=%{http_code}\n' -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/app/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222'
```

Expected result: the status is 403.

## Expected Results

The admin shell loads for `platform-admin`.

The migration workspace loads.

Navigation omits `/admin/app/patterns`.

Search omits `/admin/app/patterns`.

The retired HTML route is unavailable.

The retired JSON route returns 404.

The retired action and export routes return 404 or 405.

Bootstrap shell states include provenance metadata.

Empty shell states include truthful empty-state metadata.

Acme tenant access succeeds for Acme.

Acme tenant access fails for Globex.

No browser view renders sample pattern records.

No browser view renders sample pattern form defaults.

No browser view renders sample export references.

## Evidence To Capture

Capture a screenshot of the local login page.

Capture a screenshot of `/admin/app`.

Capture a screenshot of `/admin/app/migration`.

Capture a screenshot of the unavailable `/admin/app/patterns` route.

Save `/tmp/qa049-user-bootstrap.json`.

Save `/tmp/qa049-user-patterns-json.txt`.

Save `/tmp/qa049-user-patterns-action.txt`.

Save `/tmp/qa049-user-patterns-export.txt`.

Save `/tmp/qa049-user-cross-tenant.txt`.

Record the browser and operating system used.

Record the final pass or fail decision.

## Security And Redaction Checks

Run this scan before sharing evidence.

```bash
grep -RInE 'sk-|authorization:|bearer |BEGIN (RSA|OPENSSH|PRIVATE) KEY|raw prompt|raw completion|memory contents|provider payload|tool payload|/Users/' /tmp/qa049-user-* || true
```

Expected result: the command prints no unsafe evidence lines.

Review screenshots for raw credential values.

Review screenshots for private channel messages.

Review screenshots for raw prompts.

Review screenshots for raw memory contents.

Review screenshots for provider payloads.

Review screenshots for local absolute paths.

If any unsafe value appears, delete the evidence file and rerun after closing developer tooling or debug panels.

## Tenant Isolation Checks

Use `platform-admin` for platform review.

Use `tenant-admin-acme` for Acme review.

Use `tenant-admin-globex` only when you intentionally need Globex scope.

An Acme principal must not bootstrap Globex scope.

The retired patterns route must stay unavailable for both platform and tenant principals.

The command search must not add the patterns route for tenant scope.

The bootstrap payload must not show unauthorized tenant labels in error text.

The cross-tenant denial output should be saved in `/tmp/qa049-user-cross-tenant.txt`.

## Troubleshooting

If local login is missing principals, recopy `.env.qa049` and restart the API.

If the database does not exist, rerun the reset and migration commands.

If `/admin/app` shows stale assets, rebuild `frontend/admin`.

If `/admin/app/patterns` renders a sample page, stop and rerun the route integration tests.

If `/admin/app/patterns/actions/sample` returns 405, that is acceptable for a retired POST route.

If command search returns a patterns result, rerun the bootstrap and search API checks.

If screenshots contain local filesystem paths, retake them without developer tooling open.

If the API port is busy, stop the old process and restart qa049.

If a reviewer is unsure whether a status is expected, compare with `qa049.md`.
