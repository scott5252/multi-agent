# QA044 UI: Operations, Reliability, Run Inspection, And Usage Full React Parity

## Goal

This browser-first walkthrough helps a reviewer verify that Spec 044 moved the
operations, reliability, run inspection, and usage browser experience to React
without breaking old links.

The reviewer should see the React operations workspace, React usage workspace,
safe redirects from old URLs, bounded tables, safe summaries, metadata-only
exports, and denied states that do not reveal cross-tenant data.

## How To Use This Guide

Use this guide from a fresh checkout or after running the API setup in
`qa044.md`. It repeats the setup commands so a reviewer does not need to switch
between documents.

Capture browser screenshots and reviewer notes under `/tmp/qa044-*`. Suggested
files are:

1. `/tmp/qa044-operations-screen.png`
2. `/tmp/qa044-reliability-screen.png`
3. `/tmp/qa044-run-debug-screen.png`
4. `/tmp/qa044-usage-screen.png`
5. `/tmp/qa044-legacy-redirect-notes.txt`

Expected: each note names the principal, URL, visible page title, and any
filters or tenant selectors used during the check.

What is happening: the reviewer is collecting evidence from the React app, not
from deleted Jinja templates.

Why this matters: Spec 044 is a migration gate, so visual evidence must prove
that old URLs and new React routes behave coherently.

## Environment Setup

Prepare the local environment:

```bash
cp specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/.env.qa044 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa044 && createdb -U postgres multi_agent_platform_qa044'
uv run alembic upgrade head
mkdir -p .data/qa044-artifacts output/playwright/qa044_ui
```

Expected: `.env` contains `AUTH_MODE=local_principal`, the database is
`multi_agent_platform_qa044`, and the artifact root is `.data/qa044-artifacts`.

What is happening: the app is configured with deterministic local principals,
mock integrations, a dedicated database, and filesystem artifact storage.

Why this matters: reviewers can safely click export, replay, and route links
without calling production providers, Telegram, credentials, or external tools.

Seed local tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa044 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex tenants exist or already existed.

What is happening: the same tenant ids used by `.env.qa044` are present in the
database.

Why this matters: tenant selectors, run links, and usage filters need stable
tenant identity to prove isolation.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` is healthy.

What is happening: FastAPI serves the React bundle and the retained JSON APIs.

Why this matters: browser checks should exercise the same app that old Jinja
routes now redirect into.

## Browser Walkthrough

1. Open local login.

   URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations`

   Action: choose `platform-admin`.

   Expected: the browser lands on `/admin/app/operations` and shows an
   Operations heading or operations workbench content.

   What is happening: local-principal auth sets the review principal cookie and
   returns directly to the React operations route.

   Why this matters: QA044 Playwright and manual UI checks depend on a browser
   session that uses platform operations permissions.

2. Review the operations overview.

   URL: `http://127.0.0.1:8000/admin/app/operations`

   Action: scan the summary cards, logs table, fallback links, and any visible
   filter controls.

   Expected: visible content is organized for React operations; no server-side
   Jinja chrome, template error, raw stack trace, provider header, raw prompt,
   or secret-like value is visible.

   What is happening: `WorkbenchPage` is loading operations summaries and safe
   navigation metadata from retained backend contracts.

   Why this matters: the React page is now the only browser destination for
   operations triage.

3. Open an old operations URL.

   URL: `http://127.0.0.1:8000/admin/operations?trace_id=trace-qa044&panel=runs`

   Action: paste the URL into the browser address bar.

   Expected: the browser redirects to `/admin/app/operations` and keeps
   `trace_id=trace-qa044` and `panel=runs` in the query string.

   What is happening: the old browser handler returns a 303 redirect rather than
   rendering `operations/index.html`.

   Why this matters: old bookmarks and saved filter links remain useful during
   the React migration.

4. Review the reliability panel.

   URL: `http://127.0.0.1:8000/admin/reliability/ui/?tenant_id=11111111-1111-1111-1111-111111111111`

   Action: follow the redirect and inspect the reliability section in React.

   Expected: the destination includes `panel=reliability`, the Acme tenant id is
   preserved, and visible action controls are either available or safely
   disabled according to the principal.

   What is happening: the reliability browser route now selects the React
   reliability panel by query state.

   Why this matters: breaker and dead-letter operations must remain governed by
   backend policy after Jinja deletion.

5. Review breaker and dead-letter direct links.

   URL: `http://127.0.0.1:8000/admin/reliability/ui/breakers?state=open`

   Action: confirm the redirect selects a breaker-oriented panel.

   Expected: the destination keeps `state=open` and `panel=breakers`.

   What is happening: filter context is carried forward for the React panel.

   Why this matters: operators should not lose incident triage context when
   opening old breaker links.

6. Review the dead-letter route.

   URL: `http://127.0.0.1:8000/admin/reliability/ui/dead-letters?status=pending`

   Action: confirm the redirect selects dead-letter content.

   Expected: the destination keeps `status=pending` and
   `panel=dead-letters`.

   What is happening: the old dead-letter browser page has been replaced by
   React query-state routing.

   Why this matters: dead-letter investigation must keep filters while avoiding
   old templates.

7. Review admin run search.

   URL: `http://127.0.0.1:8000/admin/runs?tenant_id=11111111-1111-1111-1111-111111111111`

   Action: follow the redirect and inspect the operations run panel.

   Expected: the destination is `/admin/app/operations` with `panel=runs` and
   the Acme tenant id.

   What is happening: admin run search no longer renders `runs/index.html`.

   Why this matters: run inspection is a sensitive surface and should use the
   same React authorization and redaction model as the workbench.

8. Review old replay browser handling.

   URL: use a seeded run id from the integration fixtures, or run the focused
   route tests in `qa044.md` for deterministic coverage.

   Action: inspect a browser request to `/admin/runs/{workflow_run_id}/replay`
   when a run exists and the principal is authorized.

   Expected: browser callers redirect to React replay query state, while JSON
   callers continue to receive the replay contract.

   What is happening: browser negotiation decides redirect versus JSON.

   Why this matters: API clients and React still need replay data, but Jinja
   replay pages are retired.

9. Review user-facing run compatibility.

   URL: `http://127.0.0.1:8000/runs`

   Action: open the URL while signed in as a local principal.

   Expected: the page redirects to `/admin/app/channels` or a channel run route
   without rendering a `runs` template.

   What is happening: the compatibility route sends browser users to the React
   channel workspace while retained channel APIs continue to serve run state.

   Why this matters: public run links must remain navigable without preserving
   duplicate Jinja UI.

10. Review the usage dashboard.

    URL: `http://127.0.0.1:8000/admin/usage?tenant_id=11111111-1111-1111-1111-111111111111&group_by=provider`

    Action: follow the redirect to React usage.

    Expected: the browser reaches `/admin/app/usage` with the tenant and
    grouping query values preserved.

    What is happening: usage filter state moves from the old browser handler to
    React query state.

    Why this matters: usage reviewers should not lose context when opening old
    dashboard links or saved filters.

11. Review usage export metadata.

    URL: use an export id created by the focused backend tests, or create one
    from the React usage export control in the QA database.

    Action: open `/admin/app/usage/exports/{usage_export_request_id}` and review
    the export detail fields.

    Expected: visible fields are metadata only: status, row count, checksum,
    artifact reference, filter snapshot, created time, and completed time.

    What is happening: React renders a safe export detail view without raw CSV
    rows or storage-provider internals.

    Why this matters: export metadata is useful for auditors, but raw usage rows
    and artifact contents should stay protected.

12. Switch to a tenant principal.

    URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage`

    Action: choose `tenant-admin-acme`, then open the usage page with the Acme
    tenant id and with the Globex tenant id.

    Expected: Acme is allowed and Globex fails closed or shows an authorized
    empty/denied state without exposing Globex names or rows.

    What is happening: React route context is still checked by backend tenant
    rules.

    Why this matters: old redirects must not become a cross-tenant bypass.

## Required Automated Evidence

Run focused backend checks:

```bash
uv run pytest --no-cov tests/integration/api/test_admin_operations_ui.py tests/integration/api/test_reliability_controls_ui.py tests/integration/api/test_admin_run_inspection_ui.py tests/integration/api/test_web_run_ui.py tests/integration/api/test_admin_usage_ui.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py tests/unit/admin/test_operations_jinja_retirement.py tests/unit/api/test_admin_workbench_schema.py tests/unit/api/test_admin_usage_react_schema.py tests/performance/operations/test_workbench_queries.py tests/performance/usage/test_react_usage_queries.py -q
```

Expected: all focused tests pass.

Run focused frontend checks:

```bash
cd frontend/admin
npm test -- --run src/components/workbench src/components/usage src/App.test.tsx
npm run build
cd ../..
```

Expected: React workbench, usage, and application route tests pass and the
bundle builds.

Run project quality checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/044-operations-reliability-run-inspection-and-usage-full-react-parity/validation.yml --start-processes
```

Expected: all checks pass and Playwright writes
`output/playwright/qa044_ui/qa044-react-ui2-smoke.png`.

## UI Evidence Checklist

- Screenshot `/tmp/qa044-operations-screen.png` shows the React operations page.
- Screenshot `/tmp/qa044-reliability-screen.png` shows reliability content or a
  governed unavailable state.
- Screenshot `/tmp/qa044-run-debug-screen.png` shows run search or run debug
  state in React.
- Screenshot `/tmp/qa044-usage-screen.png` shows the React usage page.
- Notes in `/tmp/qa044-legacy-redirect-notes.txt` list old URL, destination URL,
  principal, expected result, and reviewer decision.
- Evidence confirms no raw prompt, completion, memory, provider header, secret,
  private channel message, raw CSV row, or stack trace appears in browser text.
- Evidence confirms old URLs redirect instead of showing deleted Jinja pages.
- Evidence confirms tenant context is preserved or safely denied.

## Acceptance Notes Template

Use this text file shape for manual signoff:

```text
QA044 UI reviewer:
Platform login completed:
Operations React route reviewed:
Reliability redirects reviewed:
Run inspection redirects reviewed:
User-facing run redirects reviewed:
Usage React route reviewed:
Tenant isolation reviewed:
Redaction reviewed:
Screenshots captured:
Decision:
```

Expected: the completed note lists each old URL class and points to at least one
screenshot or browser note file.

What is happening: reviewer judgment is captured alongside automated evidence.

Why this matters: migration signoff needs human confirmation that browser
behavior is understandable, not only that APIs returned status codes.

## Troubleshooting

If local login loops, clear the `map_local_principal` cookie and reopen
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations`.

Expected: choosing `platform-admin` returns to the React operations workspace.

If old URLs show 404, confirm the API process restarted after the Spec 044 route
changes and the React bundle was rebuilt.

Expected: old operations, reliability, run, and usage browser URLs return 303
redirects or safe non-Jinja problems.

If the usage export detail page is empty, create an export using the React usage
workspace or run the focused backend usage route tests to create deterministic
export data.

Expected: export detail shows metadata only and no raw CSV rows.

If a browser page shows raw stack traces or secrets, stop validation and attach
the screenshot path in the blocker report.

Expected: no QA044 evidence includes sensitive payloads.

## Related Files

- `specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/qa044.md`
- `specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/.env.qa044`
- `src/multi_agent_platform/api/routers/admin_operations.py`
- `src/multi_agent_platform/api/ui/reliability_controls.py`
- `src/multi_agent_platform/api/routers/admin_run_inspection.py`
- `src/multi_agent_platform/api/routers/web_run_ui.py`
- `src/multi_agent_platform/api/routers/admin_usage.py`
- `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- `frontend/admin/src/components/usage/UsagePage.tsx`
- `tests/unit/admin/test_operations_jinja_retirement.py`
