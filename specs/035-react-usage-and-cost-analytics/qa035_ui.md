# QA035 UI Walkthrough

## Goal

QA035 UI validation proves the React usage and cost analytics page renders safe usage totals, cost estimates, confidence labels, trend buckets, rollups, event drilldowns, export evidence, and tenant-scoped denied states.

The route under review is /admin/app/usage.

The browser should show the usage analytics workspace as the first usable screen.

The browser should show sections for Usage, Usage filters, Summary, Trend, Rollups, Drilldown, and Export.

The browser should show total tokens, estimated cost, usage events, average latency, unavailable usage, and confidence coverage.

The browser should show safe labels for providers, models, workflows, agents, prompts, graph nodes, gateway operations, physical attempts, and governed tools.

The browser should not make raw identifiers the primary experience.

The browser should not show qa035-secret-value, raw prompt, raw completion, memory content, authorization header, provider token, credential value, credential reference internals, raw tool payload, private message, local filesystem path, or unauthorized tenant label.

Expected: platform screenshots can show authorized Acme and Globex labels.

Expected: tenant screenshots show Acme only.

Expected: no screenshot contains qa035-secret-value.

Expected: no screenshot contains raw prompt.

Expected: no screenshot contains raw completion.

Expected: no screenshot contains memory content.

Expected: no screenshot contains authorization header.

Expected: no screenshot contains provider token.

Expected: no screenshot contains credential value.

Expected: no screenshot contains raw tool payload.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from .env.qa035.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, confusing rollup labels, or tenant-scope uncertainty.

Do not paste secrets into the browser.

Do not paste raw prompts into reviewer notes.

Do not paste completions into reviewer notes.

Do not paste memory content into reviewer notes.

Do not paste provider headers into reviewer notes.

Do not paste raw connector payloads into reviewer notes.

Expected: QA evidence can be shared with reviewers without cleanup.

Expected: every export action is explicit and user initiated.

What is happening: the browser exercises the same React route administrators use for usage analytics.

Why this matters: UI validation catches layout, focus, and unsafe presentation issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/035-react-usage-and-cost-analytics/.env.qa035 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa035 && createdb -U postgres multi_agent_platform_qa035'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa035 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa035-artifacts output/playwright/qa035_ui
```

Expected: database, React assets, and evidence folders are ready.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: worker starts without live provider, Telegram, credential, or connector calls.

Open the local browser login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage
```

Expected: local login offers platform-admin and tenant-admin-acme.

## Browser Walkthrough

### Step 1: Denied Usage Route

Open:

```text
http://127.0.0.1:8000/admin/app/usage
```

Expected: a 401 response appears when not logged in.

Expected: no usage totals, rollups, event rows, or export references appear.

What is happening: the shell route is guarded before React usage data can render.

Why this matters: usage analytics cannot leak anonymously.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-denied.png.

### Step 2: Platform Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage
```

Choose platform-admin.

Expected: the browser redirects to /admin/app/usage.

Expected: the shell shows React Admin.

Expected: the page heading says Usage and Cost Analytics.

Expected: the page shows Total tokens.

Expected: the page shows Estimated cost.

Expected: the page shows Confidence coverage.

Expected: the page shows authorized Acme and Globex labels.

What is happening: the platform principal can review authorized cross-tenant usage summaries.

Why this matters: platform support workflows need broad visibility without unsafe run data display.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-platform.png.

### Step 3: Grouping And Rollups

Use the Group by select control.

Select Gateway operation.

Expected: the Rollups heading changes to Gateway Operation.

Expected: the table shows chat.completions primary route.

Expected: the table shows attempt attribution safely.

Select Governed tool.

Expected: the Rollups heading changes to Governed Tool.

Expected: the table shows Daily briefing calendar list or another safe tool label.

What is happening: the React selector asks the backend for safe grouping data.

Why this matters: browser code cannot infer hidden attribution from unauthorized rows.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-rollups.png.

### Step 4: Event Drilldown

Click View on the first rollup row.

Expected: the Drilldown panel shows Safe events.

Expected: event rows show timestamps, provider/model labels, workflow labels, token counts, costs, latency, and audit references.

Expected: the drilldown row count is bounded.

Expected: the drilldown does not show raw prompts or raw completions.

What is happening: the UI loads /admin/app/usage/events.json for the active safe filter snapshot.

Why this matters: reviewers can investigate cost or latency without opening raw run content.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-drilldown.png.

### Step 5: Export Evidence

Click Export CSV or Create export.

Expected: the Export panel shows completed.

Expected: the Export panel shows usage-export-artifact-qa035.

Expected: the Export panel shows audit-usage-qa035-export-created.

Expected: the Export panel shows sha256:qa035d.

Expected: the page does not render raw CSV contents.

What is happening: React posts a backend-owned safe filter snapshot to create an audited export.

Why this matters: exports must be governed evidence artifacts rather than unbounded browser-generated files.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-export.png.

### Step 6: Export Detail

Open:

```text
http://127.0.0.1:8000/admin/app/usage/exports/35000000-0000-0000-0000-000000000035
```

Expected: the export detail page shows completed.

Expected: the export detail page shows Platform.

Expected: the export detail page shows usage-export-artifact-qa035.

Expected: the export detail page shows audit-usage-qa035-export-created.

What is happening: the SPA fallback serves the React detail route and the detail component loads safe export metadata.

Why this matters: reviewers can revisit export evidence without reading local storage paths or raw CSV contents.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-export-detail.png.

### Step 7: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111
```

Choose tenant-admin-acme.

Expected: the browser redirects to /admin/app/usage for the Acme tenant.

Expected: the page shows Acme.

Expected: the page does not show Globex.

Expected: the group selector does not offer tenant-wide cross-tenant review to the tenant admin.

Expected: export actions remain scoped to Acme.

What is happening: tenant visibility is constrained by the authenticated principal and active tenant scope.

Why this matters: tenant administrators cannot inspect other tenants' usage rows or export metadata.

Screenshot evidence: output/playwright/qa035_ui/qa035-react-usage-tenant.png.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/035-react-usage-and-cost-analytics
```

Run static checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Run full coverage:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run Playwright UI validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml --start-processes
```

Run frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Expected: screenshots are written under output/playwright/qa035_ui.

Expected: browser automation logs do not contain unsafe usage content.

## UI Evidence Checklist

- Denied route screenshot captured.
- Platform dashboard screenshot captured.
- Gateway or governed tool rollup screenshot captured.
- Event drilldown screenshot captured.
- Export summary screenshot captured.
- Export detail screenshot captured.
- Tenant dashboard screenshot captured.
- Platform screenshot may include Acme and Globex.
- Tenant screenshot includes Acme only.
- No screenshot shows fake secret values.
- No screenshot shows raw prompts.
- No screenshot shows raw completions.
- No screenshot shows memory content.
- No screenshot shows provider headers.
- No screenshot shows local filesystem paths.

Expected: every screenshot can be shared with a reviewer without masking.

## Acceptance Notes Template

Use this note format:

```text
QA035 UI reviewer:
Browser:
Route:
Platform screenshot:
Rollup screenshot:
Drilldown screenshot:
Export screenshot:
Tenant screenshot:
Redaction result:
Layout concerns:
Decision:
```

What is happening: reviewer notes bind each expected state to a concrete screenshot.

Why this matters: later reviewers can understand what was manually checked without rerunning the browser.

## Troubleshooting

If the local login page does not list platform-admin, confirm .env.qa035 was copied and the API restarted.

If the page shows React admin unavailable, rebuild the React assets and reload.

If Usage and Cost Analytics does not appear, confirm the principal has usage:read.

If Group by does not update, check the browser network request to /admin/app/usage/bootstrap.json.

If the View button does not change drilldown rows, verify the events API returns rows for the selected rollup.

If export detail returns 404, confirm the SPA fallback allows usage export detail routes.

If tenant-admin-acme sees Globex, stop and treat it as a tenant isolation failure.

If a screenshot contains unsafe content, delete the screenshot, fix the rendering path, and recapture evidence.

Expected: troubleshooting stays local and deterministic.

## Related Files

- specs/035-react-usage-and-cost-analytics/qa035.md.
- specs/035-react-usage-and-cost-analytics/qa035_user_guide.md.
- specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml.
- frontend/admin/src/components/usage/UsagePage.tsx.
- frontend/admin/src/components/usage/UsageRollupPanel.tsx.
- frontend/admin/src/components/usage/UsageEventDrilldown.tsx.
- frontend/admin/src/components/usage/UsageExportPanel.tsx.
- frontend/admin/src/components/usage/UsageExportDetailPage.tsx.
