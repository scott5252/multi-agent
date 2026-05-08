# QA055 UI Walkthrough: Channels Telegram Briefing React Live Data

## Goal

Guide a reviewer through browser evidence for qa055.

Expected: the React channel workspace loads from live backend records.

Expected: the browser shows seeded Acme channel rows only after the QA seed
command persists them.

Expected: the reviewer can click `Save Preferences` and see an accepted
mutation result.

Expected: the post-UI verifier proves a new briefing preference revision exists
in the qa055 database after the browser action.

Expected: the browser never displays bot tokens, webhook secrets, full Telegram
identifiers, raw messages, raw preferences, raw run payloads, provider tokens,
credential values, local paths, stack traces, or unauthorized tenant content.

What is happening: the page is using `/admin/app/channels/bootstrap.json` and
briefing mutation routes rather than fixed production helper rows.

Why this matters: qa055 is only done if browser-visible data is backed by the
same database rows the API and verifier inspect.

## How To Use This Guide

Use this walkthrough with `qa055.md`.

Save screenshots under `output/playwright/qa055_ui`.

Save reviewer notes under `/tmp/qa055-ui-reviewer-notes.txt`.

Save browser console notes under `/tmp/qa055-ui-console-notes.txt`.

Save post-action API notes under `/tmp/qa055-ui-post-api-notes.txt`.

Expected: screenshot filenames include qa055.

Expected: notes mention the local principal and tenant being reviewed.

Expected: API notes identify the preference revision by safe revision or audit
reference only.

Expected: reviewer notes avoid copying unsafe payload content.

What is happening: automated Playwright follows the same flow as this manual
walkthrough.

Why this matters: manual evidence and automated evidence should match.

## Environment Setup

Copy the QA environment.

```bash
cp specs/055-channels-telegram-briefing-react-live-data/.env.qa055 .env
```

Expected: `.env` now contains `APP_NAME=multi-agent-platform-qa055`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are available.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL service is running.

Reset the qa055 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa055 && createdb -U postgres multi_agent_platform_qa055'
```

Expected: only the qa055 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete successfully.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa055 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist.

Seed channel and briefing records.

```bash
uv run python scripts/qa/seed_channels_briefing_qa055.py
```

Expected: the command prints the seeded qa055 tenant id and run id.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

Run the required quality commands when capturing final evidence.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: backend quality gates pass.

Run the frontend checks when capturing final evidence.

```bash
npm run --prefix frontend/admin test -- --run ChannelTelegramBriefing
npm run --prefix frontend/admin typecheck
npm run --prefix frontend/admin build
```

Expected: channel UI tests, typecheck, and build pass.

## Browser Walkthrough

Open the local login route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Expected: the local-principal login page appears.

Choose the Acme tenant user principal.

```text
tenant-user-acme
```

Expected: the browser redirects to `/admin/app/channels`.

Confirm the page title.

```text
Channel, Telegram, and Briefing Preferences
```

Expected: the page title is visible.

Confirm the active scope.

```text
Active scope: Acme
```

Expected: the page is scoped to Acme.

Confirm briefing preference evidence.

```text
Metro area summary
```

Expected: the seeded briefing profile appears with safe summaries.

Confirm the timezone.

```text
America/New_York
```

Expected: the current user preference profile is rendered.

Confirm linked identity evidence.

```text
Telegram user tg-***-1055
```

Expected: the Telegram user is masked.

Confirm chat evidence.

```text
Chat chat-***-4055
```

Expected: the Telegram chat is masked.

Click `Save Preferences`.

```text
Save Preferences
```

Expected: the page shows `Preference profile saved with redacted summaries.`.

What is happening: the browser posts to the briefing preference save endpoint
with the active profile revision.

Why this matters: the mutation result is produced by the backend service and is
not a browser-only success message.

Capture a screenshot.

```bash
mkdir -p output/playwright/qa055_ui
```

Expected: screenshot evidence is stored under `output/playwright/qa055_ui`.

Run post-UI verification.

```bash
uv run python scripts/qa/verify_channels_briefing_qa055.py | tee /tmp/qa055-post-ui-evidence.txt
```

Expected: the verifier reports at least two briefing revisions.

Expected: the verifier reports at least one `profile_updated` audit.

What is happening: the verifier checks persisted database rows after the UI
action.

Why this matters: a screenshot alone does not prove the live-data replacement.

## Admin Browser Checks

Open the local login route again.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Expected: the login page is available for another principal.

Choose the Acme tenant admin principal.

```text
tenant-admin-acme
```

Expected: the browser redirects to the channel workspace.

Confirm alias evidence.

```text
Morning briefing
```

Expected: the alias is visible only for the Acme tenant.

Confirm the target summary.

```text
Configured workflow
```

Expected: the alias target is a safe live summary.

Confirm delivery diagnostics.

```text
Delivery Diagnostics
```

Expected: the delivery panel is visible to the tenant admin.

Confirm delivery status.

```text
delivered
```

Expected: the delivered attempt is shown without raw Telegram payloads.

Click `Create Code` only during manual review when a one-time token can be
captured safely.

```text
Create Code
```

Expected: the token appears once and future dashboard loads show masked audit
status only.

What is happening: tenant administrators can exercise Telegram actions through
backend-owned routes.

Why this matters: admin actions must not leak reusable secrets or raw Telegram
identifiers.

## Required Automated Evidence

Run the qa055 Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml --start-processes
```

Expected: the flow clicks `Save Preferences`.

Expected: the flow sees the saved preference mutation result.

Expected: the flow writes `qa055-live-data-ui-api-smoke.png`.

Run the post-UI verifier after Playwright.

```bash
uv run python scripts/qa/verify_channels_briefing_qa055.py
```

Expected: database evidence matches the browser action.

Run curl regression after qa055 validation.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa055-after-spec
```

Expected: curl regression uses its own database and passes independently.

## UI Evidence Checklist

Record the signed-in principal.

```text
Principal:
Tenant:
Browser route:
Screenshot:
```

Expected: the principal is either `tenant-user-acme` for preference save or
`tenant-admin-acme` for admin diagnostics.

Record visible channel rows.

```text
Alias:
Linked identity:
Delivery status:
Run id:
Preference revision:
```

Expected: visible values are safe labels, masked identifiers, or redacted
summaries.

Record unsafe text review.

```text
Bot token shown:
Webhook secret shown:
Raw Telegram id shown:
Raw preference shown:
Unauthorized tenant shown:
```

Expected: every unsafe text check is `no`.

What is happening: the reviewer is checking visual evidence and redaction at
the same time.

Why this matters: qa055 removes fixed data without weakening safety boundaries.

## Acceptance Notes Template

Use this template in reviewer notes.

```text
QA055 browser route passed:
Preference save clicked:
Post-UI verifier passed:
Screenshot path:
Unexpected behavior:
```

Expected: unexpected behavior is either empty or linked to a focused issue.

Use this template for tenant isolation.

```text
Acme seeded rows visible:
Globex empty state visible:
Acme rows absent from Globex:
Unsafe text absent:
```

Expected: Acme and Globex evidence stays separated.

What is happening: the acceptance note captures the core live-data proof.

Why this matters: the next spec should not start until this proof is complete.

## Troubleshooting

If the page stays on loading, check `/tmp/qa055-api.log`.

If the page has no Acme briefing profile, rerun the seed script and reload.

If `Save Preferences` is missing, confirm the signed-in principal is
`tenant-user-acme`.

If the page shows `not configured`, confirm the qa055 Telegram references are
present in `.env.qa055`.

If the verifier reports only one revision, rerun Playwright and inspect the
browser for the accepted mutation text.

Expected: focused repair remains limited to qa055 route, seed, verifier, docs,
or validation manifest files.

What is happening: troubleshooting directs the reviewer to the exact layer that
can fail.

Why this matters: unrelated dirty worktree changes should remain intact while
the autopilot continues.

## Related Files

- `specs/055-channels-telegram-briefing-react-live-data/qa055.md`
- `specs/055-channels-telegram-briefing-react-live-data/.env.qa055`
- `specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml`
- `scripts/qa/seed_channels_briefing_qa055.py`
- `scripts/qa/verify_channels_briefing_qa055.py`
- `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`
- `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`
