# QA055 User Guide: Spec 055 - Channels, Telegram, Briefing React Live Data

## Detailed Overview

QA055 verifies that the channel, Telegram, and briefing workspace is no longer
using fixed React payloads from the earlier QA036 implementation.

The workspace now reads persisted records for Telegram tenant configuration,
command aliases, linked identities, link-token audits, webhook diagnostics,
delivery attempts, workflow runs, and briefing preference profiles.

The most important proof is simple: when the qa055 database is empty, the page
shows an empty state; when the qa055 seed script inserts rows, the page shows
only those rows.

The second proof is a browser action. The reviewer saves briefing preferences
from the React page, then a verifier script checks the database for a new
preference revision and an audit event.

The third proof is redaction. The page must show masked Telegram labels,
safe summaries, trace references, audit references, and artifact references
only.

It must not show reusable secrets, raw Telegram identifiers, raw messages, raw
briefing preferences, raw run payloads, provider tokens, credential values,
local filesystem paths, stack traces, or unauthorized tenant labels.

This guide is written for manual QA reviewers who may not work in the codebase
every day.

The automated validation does the same checks with scripts and Playwright, but
manual review is useful when confirming the browser experience and evidence
quality.

## Who Should Use This Guide

Use this guide if you are validating Spec 055 locally.

Use it if you need to confirm that the React channel workspace is using live
database records.

Use it if you need to collect reviewer notes for the remove-mock-data roadmap.

Use it if a Playwright run fails and you need to understand what the browser
was trying to prove.

Use it if you want to compare Acme seeded data with Globex empty state data.

You do not need real Auth0 access.

You do not need a real Telegram bot.

You do not need live provider credentials.

You do need local PostgreSQL, Python dependencies from `uv sync`, and the
repository checkout.

## Manual QA Prerequisites

Start from the repository root.

Make sure no production environment file is being used.

Copy the qa055 environment file.

```bash
cp specs/055-channels-telegram-briefing-react-live-data/.env.qa055 .env
```

Expected result: `.env` uses `multi_agent_platform_qa055`.

Install dependencies.

```bash
uv sync
```

Expected result: dependencies install successfully.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: the local PostgreSQL container is running.

Recreate only the qa055 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa055 && createdb -U postgres multi_agent_platform_qa055'
```

Expected result: no database other than `multi_agent_platform_qa055` is reset.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations complete.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa055 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected result: Acme and Globex are available.

Seed the qa055 live records.

```bash
uv run python scripts/qa/seed_channels_briefing_qa055.py
```

Expected result: the command prints the Acme tenant id, workflow version id,
briefing profile id, alias id, run id, and delivery attempt id.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: `http://127.0.0.1:8000/health/live` is healthy.

## Step-by-Step Manual QA

Open the local login page in a browser.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Select `tenant-user-acme`.

Expected result: the browser opens the channel workspace for Acme.

Confirm the main title reads `Channel, Telegram, and Briefing Preferences`.

Expected result: the title is visible near the top of the page.

Confirm the active scope reads `Acme`.

Expected result: the page does not show Globex data in the Acme scope.

Find the briefing preference section.

Expected result: the page shows `Metro area summary`.

Confirm the timezone.

Expected result: `America/New_York` is visible.

Confirm the scheduled time summary.

Expected result: the preference profile shows `07:45` as a safe summary.

Click `Save Preferences`.

Expected result: the page shows `Preference profile saved with redacted summaries.`.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_channels_briefing_qa055.py
```

Expected result: the verifier reports at least two briefing revisions and at
least one profile updated audit.

Open the local login page again.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Select `tenant-admin-acme`.

Expected result: the admin view opens for Acme.

Confirm the alias section.

Expected result: `Morning briefing` is visible.

Confirm the alias target summary.

Expected result: `Configured workflow` is visible.

Confirm linked identity evidence.

Expected result: the page shows masked Telegram labels such as `tg-***-1055`
and `chat-***-4055`.

Confirm delivery diagnostics.

Expected result: the page shows a delivered Telegram notification attempt.

Confirm run status evidence.

Expected result: the seeded run id `55555555-5555-4555-8555-555555555555` can
be opened through the run status link.

Open the local login page a third time.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Select `tenant-admin-globex`.

Expected result: the page is scoped to Globex.

Confirm empty state behavior.

Expected result: Globex shows no Acme alias, no Acme run id, and no Acme
briefing profile.

## Expected Results

The Acme tenant user can save briefing preferences.

The Acme tenant admin can review Telegram configuration, alias, identity,
delivery, webhook, and run evidence.

The Globex tenant admin sees an empty or unavailable state for rows that were
not seeded for Globex.

The page never renders `qa036-secret-value`.

The page never renders `pair-code`.

The page never renders raw Telegram user ids or raw Telegram chat ids.

The page never renders raw message text.

The page never renders raw briefing preferences.

The page never renders raw run payloads.

The page never renders provider tokens or credential values.

The page never renders unauthorized tenant content.

The post-UI verifier passes after the browser save.

The Playwright screenshot lands under `output/playwright/qa055_ui`.

## Evidence To Capture

Capture the Acme tenant-user screenshot after saving preferences.

Capture the Acme tenant-admin screenshot showing alias and delivery evidence.

Capture the Globex tenant-admin screenshot showing empty state behavior.

Save API evidence in `/tmp/qa055-api-evidence.txt`.

Save quality command output in `/tmp/qa055-quality-evidence.txt`.

Save post-UI verifier output in `/tmp/qa055-post-ui-evidence.txt`.

Record the principal used for each screenshot.

Record whether unsafe markers were absent.

Record whether the post-UI verifier saw the profile update audit.

Record the curl regression output directory `.data/curl_test_runs/qa055-after-spec`.

## Security And Redaction Checks

Check for bot token text.

Expected result: no bot token value appears.

Check for webhook secret text.

Expected result: no webhook secret appears.

Check for raw Telegram identifiers.

Expected result: only masked labels appear.

Check for raw briefing preference values.

Expected result: preference output uses safe summaries.

Check for raw run payloads.

Expected result: run output uses safe status labels and trace references.

Check for local filesystem paths.

Expected result: no local path appears in browser output.

Check for stack traces.

Expected result: no stack trace appears in browser output.

## Tenant Isolation Checks

Use `tenant-admin-acme` for the seeded tenant.

Expected result: Acme shows `Morning briefing`.

Use `tenant-admin-globex` for the unseeded tenant.

Expected result: Globex does not show `Morning briefing`.

Use the Acme bootstrap API route.

Expected result: Acme bootstrap contains the seeded run id.

Use the Globex bootstrap API route.

Expected result: Globex bootstrap does not contain the seeded run id.

Use the tenant-user principal for preference save.

Expected result: the profile update is scoped to Acme and `tenant-user-acme`.

## Troubleshooting

If the page is blank, confirm the built React assets are available.

If the page cannot load bootstrap JSON, check `/tmp/qa055-api.log`.

If the page says configuration is unavailable, confirm `.env.qa055` was copied
to `.env`.

If seeded rows are missing, rerun `uv run python scripts/qa/seed_channels_briefing_qa055.py`.

If the preference save button is missing, confirm you selected
`tenant-user-acme`.

If the verifier fails on revision count, rerun the browser save and verify the
accepted mutation result is visible.

If Globex shows Acme rows, stop and treat it as a tenant isolation blocker.

If any raw secret, raw Telegram id, raw preference, or raw run payload appears,
stop and treat it as a security blocker.

If curl regression fails after qa055 validation, inspect the curl output
directory before advancing to the next spec.
