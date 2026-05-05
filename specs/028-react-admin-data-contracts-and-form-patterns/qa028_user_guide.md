# QA028 User Guide: Spec 028 - React Admin Data Contracts And Form Patterns

## Detailed Overview

QA028 reviews a safe React admin patterns page.

The page lives at `/admin/app/patterns`.

It is not a production workflow page.

It is a reusable example for later React admin migrations.

The page shows how React should receive data from FastAPI.

FastAPI sends one authorized page envelope.

That envelope includes page title text.

That envelope includes sample records.

That envelope includes allowed filters.

That envelope includes sorting metadata.

That envelope includes form fields.

That envelope includes safe action URLs.

That envelope includes export status.

That envelope includes safe evidence summaries.

React renders those values.

React does not decide who can see a tenant.

React does not decide which filters are allowed.

React does not build hidden export paths.

React does not show secrets.

React does not show raw prompts.

React does not show provider payloads.

React does not show memory contents.

React does not show external tool payloads.

The page has a table named `Sample records`.

The page has a form named `Sample action`.

The page has a button named `Preview result`.

The page has a button named `Export preview`.

The sample form can preview several safe outcomes.

A blank sample name shows field validation.

The `stale` outcome shows revision conflict guidance.

The `replay` outcome shows idempotency replay guidance.

The `confirmation` outcome shows a confirmation prompt.

The normal outcome shows accepted feedback.

Every result is harmless.

No real domain record is changed.

No real provider is called.

No Telegram message is sent.

No external connector is called.

Expected result: reviewers can see a complete pattern without risking real data.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA028.

Use this guide if you are verifying the React admin page in a browser.

Use this guide if you need plain-language acceptance notes.

Use this guide if you are checking tenant isolation.

Use this guide if you are checking redaction.

Use this guide if you are checking form behavior.

Use this guide if you are checking export safety.

You do not need to understand React internals.

You do not need to understand SQLAlchemy internals.

You do need access to the local repository.

You do need the local QA database.

You do need a browser.

You do need the `tenant-admin-acme` local login option.

You should stop if the page asks for real credentials.

You should stop if a command points at production.

You should stop if a page shows a secret value.

You should stop if an Acme login shows Globex records.

## Manual QA Prerequisites

Start from the repository root.

Use the QA028 environment file.

Copy it into place before starting the app.

Run this command:

```bash
cp specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028 .env
```

Expected result: `.env` references `multi_agent_platform_qa028`.

Expected result: `.env` references `.data/qa028-artifacts`.

Expected result: `.env` uses only fake `qa028/` secret references.

Install Python dependencies:

```bash
uv sync
```

Expected result: dependency installation completes.

Build the React admin assets:

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Expected result: the React manifest is written under `src/multi_agent_platform/web_admin/static/react`.

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running locally.

Reset the QA028 database:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa028 && createdb -U postgres multi_agent_platform_qa028'
```

Expected result: only `multi_agent_platform_qa028` is recreated.

Apply migrations:

```bash
uv run alembic upgrade head
```

Expected result: Alembic reaches the latest migration.

Seed the local tenant rows:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa028 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected result: Acme and Globex tenant rows exist for isolation checks.

Create evidence directories:

```bash
mkdir -p .data/qa028-artifacts output/playwright/qa028_ui
```

Expected result: local evidence folders exist.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: `http://127.0.0.1:8000/health/live` responds.

Start the worker in another terminal if you are running the full local stack:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected result: the worker starts without live provider calls.

## Step-by-Step Manual QA

Step 1: check the denied route.

Open this URL before signing in:

```text
http://127.0.0.1:8000/admin/app/patterns
```

Expected result: the page shows an unauthorized response.

Expected result: no sample table is visible.

Expected result: no sample form is visible.

Expected result: no export artifact reference is visible.

What this proves: the React route fails closed before rendering contract data.

Step 2: sign in with the Acme tenant admin.

Open this URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/patterns
```

Choose `tenant-admin-acme`.

Expected result: the browser opens `/admin/app/patterns`.

Expected result: the shell says `React Admin`.

Expected result: the active scope says `Acme`.

What this proves: the page is reachable through the normal local admin path.

Step 3: review the page title.

Find `Forms and data patterns`.

Expected result: the title is visible near the top of the main content.

Expected result: the page describes harmless sample contracts.

Expected result: the page does not show a raw JSON blob.

What this proves: React renders the backend-owned page envelope as admin UI.

Step 4: review the table.

Find `Sample records`.

Expected result: `Workflow readiness review` is visible.

Expected result: `Credential policy review` is visible.

Expected result: `Export safety preview` is visible.

Expected result: status badges are readable.

Expected result: the scope column shows Acme.

What this proves: table rows are scoped to the active tenant.

Step 5: review the filter controls.

Find the status filter options.

Expected result: `Ready` is visible.

Expected result: `Needs review` is visible.

Expected result: `Paused` is visible.

Expected result: there is no unsafe free-form filter box.

Click `Ready`.

Expected result: the filtered page shows `Status: ready`.

Expected result: only matching sample records remain.

What this proves: filters come from backend-approved choices.

Step 6: review form validation.

Find `Sample action`.

Leave `Sample name` blank.

Click `Preview result`.

Expected result: `validation error` appears.

Expected result: `Enter a sample name.` appears near the field.

Expected result: no stack trace appears.

Expected result: no raw request payload appears.

What this proves: backend field validation maps safely to form controls.

Step 7: review stale conflict feedback.

Type `Preview` into `Sample name`.

Type `stale` into `Outcome`.

Click `Preview result`.

Expected result: `stale conflict` appears.

Expected result: `The sample has a newer safe revision.` appears.

Expected result: the message is understandable without exposing raw state.

What this proves: future forms can recover from optimistic concurrency failures.

Step 8: review replay feedback.

Keep `Sample name` populated.

Type `replay` into `Outcome`.

Click `Preview result`.

Expected result: `replayed` appears.

Expected result: `No duplicate side effect was applied.` appears.

Expected result: no raw idempotency request body appears.

What this proves: repeated submissions can be explained safely to admins.

Step 9: review confirmation feedback.

Keep `Sample name` populated.

Type `confirmation` into `Outcome`.

Click `Preview result`.

Expected result: `confirmation required` appears.

Expected result: `Confirm preview` appears.

Click `Confirm preview`.

Click `Preview result` again.

Expected result: the result can proceed after the user confirms.

What this proves: confirmation prompts can be represented by contract metadata.

Step 10: review accepted feedback.

Type `accepted` into `Outcome`.

Click `Preview result`.

Expected result: `accepted` appears.

Expected result: the sample says no domain side effects were applied.

What this proves: safe success messages are supported.

Step 11: review export safety.

Click `Export preview`.

Expected result: `Sample export snapshot is ready as a safe artifact reference.` appears.

Expected result: `artifact-ref-qa028-tenant` appears.

Expected result: no `/Users/` path appears.

Expected result: no raw exported file contents appear.

What this proves: React shows a safe artifact reference instead of local paths.

Step 12: review mobile layout.

Resize the browser below 900 pixels wide.

Expected result: navigation remains usable.

Expected result: the form fields fit their containers.

Expected result: buttons do not overlap text.

Expected result: table content remains readable.

What this proves: shared data/form patterns work in a narrow admin viewport.

Step 13: review keyboard behavior.

Press Tab through the page.

Expected result: focus reaches status filter links.

Expected result: focus reaches `Sample name`.

Expected result: focus reaches `Outcome`.

Expected result: focus reaches `Preview result`.

Expected result: focus reaches `Export preview`.

What this proves: key controls are reachable without a mouse.

## Expected Results

The denied route returns an unauthorized response.

The login route shows local principals.

The Acme tenant admin can open the patterns page.

The shell shows React Admin.

The active scope shows Acme.

The page title is `Forms and data patterns`.

The table title is `Sample records`.

The table includes `Workflow readiness review`.

The status filters are limited to approved options.

The form title is `Sample action`.

Blank `Sample name` shows field validation.

The `stale` outcome shows stale conflict guidance.

The `replay` outcome shows replay guidance.

The `confirmation` outcome shows a confirmation prompt.

The `accepted` outcome shows safe accepted feedback.

The export preview shows `artifact-ref-qa028-tenant`.

The page does not show `qa028-secret-value`.

The page does not show `/Users/`.

The page does not show Globex while signed in as Acme.

The page does not show raw prompts or completions.

The page does not show raw memory content.

The page does not show raw provider payloads.

The page does not show raw external tool payloads.

## Evidence To Capture

Capture a denied route screenshot or note.

Capture the authenticated patterns page screenshot.

Capture the validation error screenshot.

Capture the stale conflict screenshot or note.

Capture the replay screenshot or note.

Capture the confirmation screenshot or note.

Capture the export preview screenshot.

Capture a mobile layout note.

Capture a keyboard navigation note.

Save the browser and viewport used.

Save the local principal used.

Save the date of review.

Save any failing URL.

Save whether the issue happened before or after login.

Expected screenshot path: `output/playwright/qa028_ui/qa028-react-patterns-denied.png`.

Expected screenshot path: `output/playwright/qa028_ui/qa028-react-patterns-page.png`.

Expected screenshot path: `output/playwright/qa028_ui/qa028-react-patterns-validation.png`.

Expected screenshot path: `output/playwright/qa028_ui/qa028-react-patterns-stale.png`.

Expected screenshot path: `output/playwright/qa028_ui/qa028-react-patterns-export.png`.

## Security And Redaction Checks

Search the visible page for `qa028-secret-value`.

Expected result: no match.

Search the visible page for `/Users/`.

Expected result: no match.

Search the visible page for raw prompts.

Expected result: no prompt text appears.

Search the visible page for raw completions.

Expected result: no completion text appears.

Search the visible page for memory contents.

Expected result: no memory contents appear.

Search the visible page for provider authorization headers.

Expected result: no provider authorization headers appear.

Search the visible page for external tool payloads.

Expected result: no external tool payloads appear.

Review the export area.

Expected result: it shows an artifact reference ID only.

Review mutation messages.

Expected result: they are safe summaries only.

Stop the review if any secret-like value appears.

Stop the review if any raw payload appears.

## Tenant Isolation Checks

Stay signed in as `tenant-admin-acme`.

Open the patterns page.

Expected result: Acme appears as the active scope.

Expected result: Globex does not appear in table rows.

Expected result: Globex does not appear in export text.

Expected result: Globex does not appear in validation messages.

Try opening this URL in the same browser:

```text
http://127.0.0.1:8000/admin/app/patterns.json?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: access is denied.

Expected result: Globex record data is not returned.

Sign out or clear cookies before testing a different principal.

Sign in as `tenant-admin-globex` only if you are intentionally reviewing the Globex scope.

Expected result for Globex review: Globex should not see Acme-only tenant data.

What this proves: tenant scope is enforced by the backend contract endpoints.

## Troubleshooting

If the page says the local principal is missing, sign in through `/auth/local-login`.

If the local login page does not list `tenant-admin-acme`, check `.env.qa028`.

If `/admin/app/patterns` shows an old shell, rebuild React assets.

If the browser cannot connect, check that uvicorn is running on port 8000.

If the page cannot load pattern data, check `/admin/app/patterns.json` with `X-Local-Principal: tenant-admin-acme`.

If Acme returns 403, confirm the Acme tenant row was seeded.

If filters show unexpected options, fail the review and inspect backend filter profiles.

If blank sample name does not show validation, fail the form validation check.

If stale conflict shows raw revisions beyond safe labels, fail the redaction check.

If replay feedback is missing, check that `Outcome` is set to `replay`.

If confirmation feedback is missing, check that `Outcome` is set to `confirmation`.

If export preview shows a filesystem path, fail the export safety check.

If export preview shows raw file contents, fail the export safety check.

If any secret appears, fail the security check.

If any Globex text appears while signed in as Acme, fail the tenant isolation check.

If keyboard focus disappears, capture the location and fail the accessibility check.

If mobile text overlaps, capture the viewport size and fail the layout check.

If you cannot reproduce a failure after rebuilding assets, record the command history and retry from a clean browser profile.

Do not bypass authorization to make the page pass.

Do not edit `.env.qa028` to use production credentials.

Do not replace fake secret references with real values.

Do not skip the denied route check.

Do not skip tenant isolation checks.

Expected result: every issue can be investigated without weakening backend security.
