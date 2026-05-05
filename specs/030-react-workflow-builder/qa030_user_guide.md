# QA030 User Guide: Spec 030 - React Workflow Builder

## Detailed Overview

QA030 adds a React workflow builder to the admin console.

The builder is designed for tenant and platform administrators who need to draft, review, validate, and publish workflow revisions.

The first screen is the usable builder, not a landing page.

The builder shows guided draft sections.

The builder shows backend-owned reference choices.

The builder shows a graph canvas.

The builder also shows node and edge lists for keyboard review.

The builder shows validation findings from the backend.

The builder shows publish evidence and confirmation decisions from the backend.

The builder shows revision history.

The builder shows a read-only JSON preview that is already redacted.

The builder intentionally uses deterministic QA data in local validation.

The builder does not contact a live model provider.

The builder does not contact Telegram.

The builder does not run external connector tools.

The backend creates the workflow facts.

The React app displays the workflow facts.

The browser must not invent references, graph semantics, validation findings, publish readiness, evidence, revisions, or artifact references.

The page should feel like a dense authoring tool.

It should make save, validation, and publish state easy to find.

It should make graph structure understandable without requiring a mouse.

The most important safety rule is simple.

No raw sensitive workflow data should be visible.

Do not accept a screenshot that shows raw prompts.

Do not accept a screenshot that shows raw completions.

Do not accept a screenshot that shows memory contents.

Do not accept a screenshot that shows private channel messages.

Do not accept a screenshot that shows raw provider responses.

Do not accept a screenshot that shows Telegram updates.

Do not accept a screenshot that shows connector outputs.

Do not accept a screenshot that shows stack traces.

Do not accept a screenshot that shows local filesystem paths.

Do not accept a screenshot that shows `qa030-secret-value`.

Do not accept an Acme tenant screenshot that shows Globex data.

The expected draft name is `Daily briefing workflow`.

The expected current revision is `draft-rev-qa030-current`.

The expected draft id is `00000000-0000-0000-0000-000000000030`.

The expected stale evidence reference is `artifact-ref-qa030-stale-evidence`.

The expected JSON preview reference is `artifact-ref-qa030-json-preview`.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA030 in a browser.

Use this guide if you need a plain-language checklist.

Use this guide if you are not changing code but need to verify the feature.

Use this guide if you need to compare platform and tenant behavior.

Use this guide if you need to confirm redaction and tenant isolation.

Developers should also run `qa030.md`.

UI reviewers should also run `qa030_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes the QA environment file is `.env.qa030`.

This guide assumes Acme uses tenant ID `11111111-1111-1111-1111-111111111111`.

This guide assumes Globex uses tenant ID `22222222-2222-2222-2222-222222222222`.

## Manual QA Prerequisites

Start from the repository root.

Copy the environment file.

```bash
cp specs/030-react-workflow-builder/.env.qa030 .env
```

Install dependencies.

```bash
uv sync
```

Build the React admin bundle.

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Reset the QA030 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa030 && createdb -U postgres multi_agent_platform_qa030'
```

Run migrations.

```bash
uv run alembic upgrade head
```

Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa030 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence directories.

```bash
mkdir -p .data/qa030-artifacts output/playwright/qa030_ui
```

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Confirm the API is live.

```text
http://127.0.0.1:8000/health/live
```

Expected result: the health endpoint responds.

Expected result: local login shows `platform-admin`, `auditor`, `tenant-admin-acme`, and `tenant-admin-globex`.

## Step-by-Step Manual QA

Step 1: open the denied route.

```text
http://127.0.0.1:8000/admin/app/workflows
```

Expected result: the route is not accessible before login.

Expected result: no workflow builder content appears.

Step 2: open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Choose `tenant-admin-acme`.

Expected result: the browser redirects to `/admin/app/workflows`.

Expected result: the shell says `React Admin`.

Expected result: the page says `Workflow builder`.

Expected result: the active scope is Acme.

Step 3: review guided sections.

Find `Metadata`.

Find `References`.

Find `Graph`.

Find `Publish`.

Expected result: each section has status context.

Expected result: the draft facts show the current revision and workflow lineage.

Step 4: review authoring fields.

Find the `Name` field.

Find the `Description` field.

Find the `Join policy` select.

Expected result: changing a field marks the draft dirty.

Expected result: `Save draft` remains explicit.

Step 5: save the draft.

Click `Save draft`.

Expected result: the page shows `accepted`.

Expected result: the page shows `audit-workflow-save-qa030`.

Step 6: simulate a stale revision.

Click `Simulate stale save`.

Expected result: the page shows `stale_conflict`.

Expected result: the page tells the user to reload before saving again.

Step 7: review reference selections.

Find `Pinned runtime inputs`.

Find `Daily briefing prompt`.

Find `Briefing runtime profile`.

Find `Pinned briefing model route`.

Find `Weather connector skill`.

Find `Daily briefing required suite`.

Expected result: only safe summaries are visible.

Expected result: no raw prompt text is visible.

Step 8: review graph structure.

Find `Runtime structure`.

Find `Start briefing`.

Find `Calendar branch`.

Find `Weather branch`.

Find `Join briefing branches`.

Find `Edges and joins`.

Expected result: the graph canvas is visible.

Expected result: the node and edge lists are visible.

Step 9: run validation.

Click `Run validation`.

Expected result: the page shows a blocking finding for stale required evidence.

Click `Mark evidence current`.

Expected result: the page shows a publish confirmation requirement.

Step 10: review publish evidence.

Find `Evidence and decision`.

Find `Daily briefing required suite`.

Find `artifact-ref-qa030-stale-evidence`.

Expected result: evidence is an artifact reference, not a local path.

Step 11: publish the ready fixture.

Click `Prepare publish`.

Expected result: the page shows `confirmation_required`.

Click `Confirm publish`.

Expected result: the page shows `Workflow published as an immutable bundle`.

Step 12: review revisions and JSON preview.

Find `Immutable draft history`.

Find `audit-workflow-revision-current-qa030`.

Find `Read-only preview`.

Find `artifact-ref-qa030-json-preview`.

Expected result: the preview shows safe fields only.

Step 13: verify tenant isolation.

Open:

```text
http://127.0.0.1:8000/admin/app/workflows?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: the Acme admin is denied.

Expected result: `Globex` does not appear.

## Expected Results

Expected result: unauthenticated users cannot see the builder.

Expected result: tenant administrators can load `/admin/app/workflows`.

Expected result: the builder shows `Daily briefing workflow`.

Expected result: draft save returns `accepted`.

Expected result: stale save returns `stale_conflict`.

Expected result: validation shows stale required evidence until evidence is marked current.

Expected result: publish requires confirmation before an accepted publish result.

Expected result: graph canvas and graph lists are both visible.

Expected result: artifact references use `artifact-ref-qa030-*`.

Expected result: Acme users cannot see Globex builder data.

Expected result: no screenshot contains `qa030-secret-value`, raw prompts, raw completions, memory contents, private messages, raw provider responses, Telegram updates, connector outputs, stack traces, or local filesystem paths.

## Troubleshooting

If local login does not show `tenant-admin-acme`, check `LOCAL_PRINCIPAL_CATALOG_JSON` in `.env.qa030`.

If the builder route returns 401, sign in through `/auth/local-login?redirect_to=/admin/app/workflows`.

If the route returns 403 for Acme, confirm the Acme tenant row exists in `multi_agent_platform_qa030`.

If React assets are missing, rerun `cd frontend/admin && npm install && npm run build`.

If publish buttons do not update, reload the page and repeat the validation and publish steps.

If graph content is blank, confirm the browser loaded the latest built React bundle.

If unsafe text appears, stop the review and treat the run as failed.

## Final Manual Acceptance

Accept QA030 only when the page is usable on desktop and mobile widths, graph details are accessible without mouse interaction, all mutation outcomes are understandable, artifact references do not expose paths, and no unsafe raw workflow data appears anywhere in the browser.
