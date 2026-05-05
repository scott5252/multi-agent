# QA035 User Guide: Spec 035 - React Usage And Cost Analytics

## Detailed Overview

This guide explains how to manually review the React usage and cost analytics workspace.

The workspace helps administrators understand recent model usage and estimated cost.

The main screen is /admin/app/usage.

The screen is built for platform administrators and tenant administrators.

Platform administrators can review authorized platform-wide usage.

Tenant administrators can review only their own tenant's usage.

The default view covers the last 7 days.

The page includes a header, filters, summary cards, a trend chart, rollup rows, event drilldowns, and export evidence.

Summary cards answer the first administrative questions.

The cards show token totals, estimated cost, event count, average latency, unavailable usage, and confidence coverage.

The trend chart shows how usage changed across the selected range.

Rollups let reviewers compare providers, models, workflows, agents, prompts, graph nodes, gateway operations, physical attempts, and governed tools.

The drilldown panel shows bounded event rows.

The export panel creates safe CSV evidence for the active filter snapshot.

The export detail page lets reviewers revisit export metadata later.

The browser must never show raw prompts.

The browser must never show raw completions.

The browser must never show memory content.

The browser must never show secrets.

The browser must never show provider credentials.

The browser must never show provider authorization headers.

The browser must never show raw tool payloads.

The browser must never show unauthorized tenant labels.

The browser must never show local filesystem paths.

The local QA environment uses deterministic fixtures.

The local QA environment does not call live model providers.

The local QA environment does not call live Auth0.

The local QA environment does not call Telegram.

The local QA environment does not call external connector tools.

Expected: the platform dashboard can show Acme and Globex because platform review is authorized.

Expected: the Acme tenant dashboard shows Acme only.

Expected: exports show artifact references and audit references instead of raw CSV contents.

Expected: denied export requests show safe denial messages.

What this proves: a non-developer reviewer can confirm the feature is useful while preserving tenant isolation and redaction.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA035.

Use this guide if you are validating the React usage analytics screen before merge.

Use this guide if you are checking whether a tenant administrator can see only tenant-scoped analytics.

Use this guide if you are checking whether platform administrators can see authorized cross-tenant rollups.

Use this guide if you are checking redaction in screenshots.

Use this guide if you are collecting reviewer notes for a pull request.

You do not need to understand model provider internals.

You do not need to understand database migrations.

You do not need to inspect raw usage records.

You do need to follow the local login steps carefully.

You do need to record which screenshots you captured.

You do need to stop immediately if tenant isolation fails.

You do need to stop immediately if unsafe content appears.

Expected: this guide can be followed by QA reviewers, product reviewers, and engineering reviewers.

## Manual QA Prerequisites

Start from the repository root.

Use the QA035 environment file.

Do not use a personal credential file.

Do not connect the app to a live provider account.

Copy the environment file:

```bash
cp specs/035-react-usage-and-cost-analytics/.env.qa035 .env
```

Install dependencies:

```bash
uv sync
```

Build React assets:

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Start PostgreSQL and reset the QA035 database:

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa035 && createdb -U postgres multi_agent_platform_qa035'
uv run alembic upgrade head
```

Seed local tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa035 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence folders:

```bash
mkdir -p .data/qa035-artifacts output/playwright/qa035_ui
```

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the API health endpoint is available.

Expected: the worker starts without live provider calls.

Expected: the local login page is available at http://127.0.0.1:8000/auth/local-login.

## Step-by-Step Manual QA

Step 1: Open the protected route while signed out.

Navigate to:

```text
http://127.0.0.1:8000/admin/app/usage
```

Expected: the route is not available anonymously.

Expected: no usage data appears.

Capture a denied route screenshot if the browser displays a visible response.

Step 2: Sign in as the platform administrator.

Navigate to:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage
```

Choose platform-admin.

Expected: the browser opens /admin/app/usage.

Expected: the page title is Usage and Cost Analytics.

Expected: the header shows the active platform scope.

Expected: the selected range says Last 7 days.

Capture output/playwright/qa035_ui/qa035-react-usage-platform.png.

Step 3: Review the summary cards.

Look for Total tokens.

Look for Estimated cost.

Look for Usage events.

Look for Average latency.

Look for Unavailable usage.

Look for Confidence coverage.

Expected: values are readable without scientific notation.

Expected: cost values use backend-owned currency formatting.

Expected: confidence labels use confirmed, estimated, partial, or unavailable.

Expected: no card shows raw run content.

Step 4: Review the trend panel.

Find the trend section.

Check that daily labels are visible.

Check that token and cost context is visible.

Check that unavailable usage remains labeled.

Expected: trend information is understandable without relying only on color.

Expected: trend buckets do not expose event payloads.

Step 5: Review provider or model rollups.

Use the Group by selector.

Choose Provider.

Expected: rows show provider labels such as OpenAI or Local compatible.

Choose Model.

Expected: rows show safe model labels.

Expected: rows show event count, tokens, cost, latency, status, attribution, and View actions.

Capture output/playwright/qa035_ui/qa035-react-usage-provider-rollup.png if doing a manual screenshot set.

Step 6: Review gateway and attempt attribution.

Choose Gateway operation.

Expected: rows distinguish gateway operations from physical attempts.

Choose Physical attempt.

Expected: rows show safe attempt summaries.

Expected: retry or unavailable attempt labels are summaries, not headers or credentials.

Step 7: Review governed tool attribution.

Choose Governed tool.

Expected: rows show safe tool labels.

Expected: rows do not show raw tool request or response payloads.

Capture output/playwright/qa035_ui/qa035-react-usage-rollups.png.

Step 8: Open a drilldown.

Click View on a rollup row.

Expected: the Safe events drilldown updates.

Expected: rows show timestamp, tenant, provider/model, workflow/agent, tokens, cost, latency, and audit evidence.

Expected: rows are bounded.

Expected: audit references are short safe references.

Expected: trace references are safe references when visible.

Capture output/playwright/qa035_ui/qa035-react-usage-drilldown.png.

Step 9: Create an export.

Click Export CSV or Create export.

Expected: the export status shows completed.

Expected: the export panel shows usage-export-artifact-qa035.

Expected: the export panel shows an audit reference.

Expected: the export panel shows a checksum prefix.

Expected: the export panel does not show raw CSV contents.

Capture output/playwright/qa035_ui/qa035-react-usage-export.png.

Step 10: Review export detail.

Open:

```text
http://127.0.0.1:8000/admin/app/usage/exports/35000000-0000-0000-0000-000000000035
```

Expected: the detail page shows completed.

Expected: the detail page shows safe scope and requester labels.

Expected: the detail page shows the same artifact reference.

Expected: the detail page shows the same audit reference.

Capture output/playwright/qa035_ui/qa035-react-usage-export-detail.png.

Step 11: Sign in as the Acme tenant administrator.

Navigate to:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111
```

Choose tenant-admin-acme.

Expected: the dashboard opens for Acme.

Expected: the page shows Acme.

Expected: the page does not show Globex.

Expected: tenant-admin-acme cannot choose a platform-wide tenant rollup.

Expected: tenant export actions remain scoped to Acme.

Capture output/playwright/qa035_ui/qa035-react-usage-tenant.png.

Step 12: Run evidence scans.

Run:

```bash
rg -n "qa035-secret-value|raw prompt|raw completion|memory content|authorization header|provider token|credential value|credential reference|raw tool payload|/Users/|unauthorized tenant label|private message" /tmp/qa035-* output/playwright/qa035_ui || true
```

Expected: the command prints no generated evidence matches.

## Expected Results

The signed-out route is denied.

The platform route loads the React admin shell.

The platform route shows Usage and Cost Analytics.

The platform route shows Acme and Globex only because platform scope is authorized.

The Acme tenant route shows Acme.

The Acme tenant route does not show Globex.

Summary cards show six primary usage health metrics.

Trend buckets are visible and understandable.

Rollup rows switch when the Group by selector changes.

Gateway operation rollups distinguish logical gateway operations.

Physical attempt rollups distinguish provider attempts.

Governed tool rollups show safe connector/tool labels.

Drilldown rows are bounded and safe.

Export creation returns completed evidence in the happy path.

Cross-tenant export attempts return denied evidence in API checks.

Export detail loads from the React route.

Screenshots are readable on desktop width.

No text overlaps or clips in the main dashboard.

No QA evidence contains unsafe markers.

## Evidence To Capture

Capture the denied route screenshot when available.

Capture the platform dashboard screenshot.

Capture a rollup screenshot after changing the group selector.

Capture a drilldown screenshot after clicking View.

Capture the export panel screenshot after creating an export.

Capture the export detail screenshot.

Capture the Acme tenant dashboard screenshot.

Save API evidence files under /tmp/qa035-* when running the automated guide.

Record whether the redaction scan printed any matches.

Record whether platform evidence includes Globex.

Record whether tenant evidence excludes Globex.

Record whether any visual layout issue appeared.

Record whether any expected limitation appeared.

Expected: evidence supports both functionality and safety review.

## Security And Redaction Checks

Check the page for fake secret values.

Check the page for raw prompts.

Check the page for raw completions.

Check the page for memory content.

Check the page for provider tokens.

Check the page for authorization headers.

Check the page for credential values.

Check the page for credential reference internals.

Check the page for raw tool payloads.

Check the page for private channel messages.

Check the page for local filesystem paths.

Check the page for unauthorized tenant labels.

Expected: none of these appear in the browser.

Expected: none of these appear in /tmp/qa035-* evidence.

Expected: none of these appear in output/playwright/qa035_ui screenshots.

## Tenant Isolation Checks

Platform administrators may see Acme.

Platform administrators may see Globex.

Tenant-admin-acme may see Acme.

Tenant-admin-acme must not see Globex.

Tenant-admin-acme must not see platform-wide tenant grouping options.

Tenant-admin-acme exports must use Acme scope.

Tenant-admin-acme cross-tenant export attempts must return denied evidence.

Tenant-admin-acme drilldowns must show only Acme event rows.

Expected: every tenant isolation check passes.

Stop the review if any tenant isolation check fails.

## Troubleshooting

If the route returns 401 after login, sign in again through the local login page.

If the route returns 403 for tenant-admin-acme, verify the Acme tenant id in the URL.

If React admin unavailable appears, rebuild frontend/admin assets.

If the Group by selector does not respond, refresh the page and check the API logs.

If export creation does not update the panel, check the network request to /admin/app/usage/exports.

If export detail returns 404, check the API route fallback and rebuild assets.

If the tenant screen shows Globex, stop the review and file a blocker.

If the redaction scan finds a match, stop the review and file a blocker.

If the trend chart appears blank, capture the screenshot and run frontend tests.

If the page text overlaps, capture the viewport size and screenshot.

Expected: troubleshooting can be completed without real external services.

Expected: blockers are limited to active Spec 035 files.
