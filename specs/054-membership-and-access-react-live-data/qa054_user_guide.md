# QA054 User Guide: Spec 054 - Membership And Access React Live Data

## Detailed Overview

QA054 validates the Membership and Access workspace in the React admin UI.

The feature removes deterministic membership rows that used to appear from
production-facing React builders.

The workspace now reads principal identities, invitations, tenant memberships,
role grants, access decisions, support overrides, and audit records from the
database.

The page must also show truthful empty states when a tenant has no live rows.

The purpose of this guide is to help a reviewer confirm that the browser, API,
and database all agree.

The main screen is `/admin/app/memberships`.

The main JSON route is `/admin/app/memberships/bootstrap.json`.

The visible browser action is the `Invite` button.

That action posts to `/admin/app/memberships/invitations`.

The action must create a persisted invitation and audit record.

The verifier script checks those rows after Playwright runs.

The QA environment uses the database `multi_agent_platform_qa054`.

The environment file is
`specs/054-membership-and-access-react-live-data/.env.qa054`.

The seed command creates Acme rows only.

The Globex tenant is present only to prove tenant isolation.

The reviewer should see Acme membership evidence when signed in as
`tenant-admin-acme`.

The reviewer should not see Acme evidence when signed in as
`tenant-admin-globex`.

Identity details should be masked.

Raw emails should not appear in response bodies or screenshots.

Provider tokens should not appear anywhere.

Credential values should not appear anywhere.

Stack traces should not appear in user-facing output.

Local filesystem paths should not appear in user-facing output.

What matters most is that membership data is live, authorized, redacted, and
durable.

## Who Should Use This Guide

Use this guide if you are manually reviewing qa054.

Use this guide if you need to reproduce Playwright evidence.

Use this guide if you need to inspect API responses safely.

Use this guide if you need to confirm tenant isolation.

Use this guide if you need to confirm redaction.

Use this guide if you need to explain the membership live-data migration to
another reviewer.

You do not need production credentials.

You do not need Auth0.

You do not need Telegram.

You do not need a live model provider.

You do need Docker or a compatible local PostgreSQL instance.

You do need the repository dependencies installed with `uv sync`.

You do need the React admin build assets available.

## Manual QA Prerequisites

Open a terminal at the repository root.

Copy the QA environment.

```bash
cp specs/054-membership-and-access-react-live-data/.env.qa054 .env
```

Expected result: `.env` points to `multi_agent_platform_qa054`.

Install dependencies.

```bash
uv sync
```

Expected result: the command finishes successfully.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running locally.

Reset the qa054 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa054 && createdb -U postgres multi_agent_platform_qa054'
```

Expected result: only the qa054 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations complete.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa054 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected result: Acme and Globex exist.

Seed membership rows.

```bash
uv run python scripts/qa/seed_membership_qa054.py
```

Expected result: the seed script prints `Seeded QA054 membership live records`.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the app serves `http://127.0.0.1:8000`.

## Step-by-Step Manual QA

Open the login URL in a browser.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Select `tenant-admin-acme`.

Expected result: the browser opens the membership workspace.

Find the heading `Membership Administration`.

Expected result: the page title is visible.

Find the directory row for `Maya Chen`.

Expected result: the seeded Acme tenant admin appears.

Find the invitation section.

Expected result: the form shows `invite.replay@example.test`.

Click `Invite`.

Expected result: the page reports `Invitation created in persisted membership state.`

Find the support override section.

Expected result: the support override panel is visible with qa054 evidence.

Find the access history section.

Expected result: the trace `trace-qa054-allow` is visible or available through
the JSON route.

Find the audit section.

Expected result: `Role grant created from qa054 live seed.` is visible.

Open a new browser session or sign out.

Open the same login URL again.

Select `tenant-admin-globex`.

Expected result: Globex does not show Acme membership records.

Open the Acme bootstrap API with the local principal header.

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/app/memberships/bootstrap.json?tenant_id=11111111-1111-1111-1111-111111111111'
```

Expected result: the response contains `Maya Chen` and no QA034 marker.

Open the Globex bootstrap API with the Globex local principal header.

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-globex' 'http://127.0.0.1:8000/admin/app/memberships/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222'
```

Expected result: the response is empty or unavailable for Globex and does not
contain Acme labels.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_membership_qa054.py
```

Expected result: the verifier reports `Verified QA054 membership live-data persistence`.

## Expected Results

The Acme membership page loads from live rows.

The Acme page shows a directory count greater than zero.

The Acme page shows invitations from persisted invitation records.

The Acme page shows role grants from persisted role grant records.

The Acme page shows membership status from persisted tenant membership records.

The Acme page shows access history from access decision records.

The Acme page shows audit rows from membership audit records.

The Acme page shows support override evidence from support override records.

The Invite action returns an accepted backend mutation result.

The verifier finds an invitation for `invite.replay@example.test`.

The verifier finds invitation audit evidence.

The verifier confirms Globex has no seeded membership rows.

The Globex page does not show `Maya Chen`.

The Globex page does not show the Acme audit summary.

The Globex page does not show the Acme support override summary.

No response contains `qa034-secret-value`.

No response contains `authorization header`.

No response contains `provider token`.

No response contains `credential value`.

No response contains `raw email`.

No response contains a stack trace.

## Evidence To Capture

Save terminal command results in `/tmp/qa054-quality-evidence.txt`.

Save API samples in `/tmp/qa054-api-evidence.txt`.

Save UI notes in `/tmp/qa054-ui-reviewer-notes.txt`.

Save post-UI verifier output in `/tmp/qa054-post-ui-evidence.txt`.

Save browser screenshots under `output/playwright/qa054_ui`.

Record the exact local principal used.

Record the active tenant label.

Record the screenshot filename.

Record the invitation result summary.

Record the verifier count summary.

Record whether Globex stayed isolated.

Do not paste raw database rows into notes.

Do not paste raw email values from database internals into notes.

Do not paste external subjects into notes unless they are already masked in the
UI.

## Security And Redaction Checks

Search browser-visible text for `raw email`.

Search browser-visible text for `full subject`.

Search browser-visible text for `authorization header`.

Search browser-visible text for `provider token`.

Search browser-visible text for `credential value`.

Search browser-visible text for `private message`.

Search browser-visible text for `stack trace`.

Search browser-visible text for `/Users/`.

Expected result: none of those strings appear.

Identity labels should be display names or masked summaries.

Email labels should be masked in route payloads.

Audit records should contain safe summaries.

Access decisions should contain safe reason categories.

Support overrides should contain safe justification summaries.

Mutation results should include safe audit references.

## Tenant Isolation Checks

Use Acme tenant id `11111111-1111-1111-1111-111111111111` for positive checks.

Use Globex tenant id `22222222-2222-2222-2222-222222222222` for isolation checks.

Acme should show seeded membership records.

Globex should not show seeded membership records.

Acme should show seeded access history.

Globex should not show Acme access history.

Acme should show seeded audit evidence.

Globex should not show Acme audit evidence.

Acme should show seeded support override evidence.

Globex should not show Acme support override evidence.

If any Acme record appears in Globex, stop validation.

If any Globex response reveals Acme counts or labels, stop validation.

## Troubleshooting

If the page does not load, confirm the API is running on port 8000.

If login choices are missing, confirm `.env` was copied from `.env.qa054`.

If Acme records are missing, rerun the seed script.

If the Invite button fails, inspect `/tmp/qa054-api.log`.

If the verifier fails, rerun Playwright or repeat the manual Invite action.

If Globex shows Acme records, report a tenant isolation blocker.

If unsafe text appears, report a redaction blocker.

If migrations fail, reset the qa054 database and rerun Alembic.

If React assets are stale, run `npm run --prefix frontend/admin build`.

If backend types look stale, run `uv run python scripts/frontend/generate_admin_react_types.py`.

If validation needs a full automated pass, run the commands in `qa054.md`.
