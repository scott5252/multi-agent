# QA017 UI Walkthrough: Telegram Configuration Console

## Flow 1: Local Login To Console

1. Start the API with `.env.qa017`.
2. Navigate to `/auth/local-login?redirect_to=/admin/telegram`.
3. Confirm the Local Login page lists `platform-admin`.
4. Click `platform-admin`.
5. Confirm `/admin/telegram` renders "Telegram Configuration".
6. Capture `01-local-login.png` and `02-telegram-configuration-console-target.png`.

## Flow 2: Direct Target

1. With the platform admin session active, navigate directly to `/admin/telegram`.
2. Confirm the admin shell navigation contains "Telegram Configuration".
3. Confirm provider readiness cards are visible.
4. Confirm the redaction notice says bot tokens, webhook secrets, private
   messages, raw prompts, and run results are excluded.
5. Capture `03-telegram-configuration-console-direct-target.png`.

## Tenant Form

1. Use the scope selector or query string to target Acme tenant scope.
2. Enable Telegram.
3. Select `/run` and `/status`.
4. Save.
5. Confirm command readiness updates without showing secrets.

## Token And Identity

1. Click "Issue link token".
2. Confirm the raw token appears once.
3. Simulate `/link <token>` through the local webhook in API QA.
4. Refresh the console.
5. Confirm linked identity rows show masked Telegram identifiers only.

## Diagnostics

1. Click "Validate webhook".
2. Confirm a diagnostic row appears.
3. Confirm `external_call_performed=false` in API output if inspected.
4. Confirm no real Telegram provider call is required.

## Goal

The goal of this UI walkthrough is to prove the browser experience is ready.
It proves local login reaches the Telegram Configuration Console.
It proves the admin shell navigation exposes the feature.
It proves provider readiness is visible.
It proves tenant controls are usable.
It proves stale conflicts are visible.
It proves link-token controls are usable.
It proves linked identities are masked.
It proves diagnostics are screenshot-safe.

## How To Use This Guide

Run this guide after copying `.env.qa017`.
Run this guide with the API listening on port 8000.
Run this guide with the local browser or Playwright.
Capture screenshots in `output/playwright/qa017_ui`.
Keep notes in `/tmp/qa017-ui-notes.txt`.
Do not use real Telegram credentials.
Do not paste private Telegram messages.
Do not include raw token values in shared notes.

## Environment Setup

Copy the environment file.

```bash
cp specs/017-telegram-configuration-console/.env.qa017 .env
```

Expected: `.env.qa017` is the source for this walkthrough.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the browser can reach `http://127.0.0.1:8000`.

Confirm the login URL.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram
```

Expected: the Local Login page opens.
What is happening: the local-principal test mode is selecting a QA admin.
Why this matters: reviewers can validate authorization without Auth0.

## Browser Walkthrough

Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram
```

Expected: the page lists `platform-admin`.
What is happening: the test catalog is available.
Why this matters: platform readiness checks require platform authority.

Click `platform-admin`.

```text
Expected target: /admin/telegram
```

Expected: the console title is `Telegram Configuration`.
What is happening: the admin shell wraps the feature route.
Why this matters: navigation and breadcrumbs should match other admin pages.

Review readiness cards.

```text
Cards: Provider readiness, Token reference, Webhook secret, Protected commands
```

Expected: readiness details are visible.
Expected: secret values are not visible.
What is happening: the page renders safe reference labels.
Why this matters: screenshots must be safe.

Select tenant scope.

```text
Tenant: Acme
```

Expected: tenant enablement controls appear.
What is happening: the page is switching from platform readiness to tenant
configuration.
Why this matters: tenant-specific Telegram access must be explicit.

Enable Telegram.

```text
Enabled: true
Commands: /run, /status
```

Expected: the save action returns to the console.
What is happening: the tenant record receives a new revision token.
Why this matters: tenant settings must not be global by accident.

Submit a stale form.

```text
Use an older revision token from a previous page view.
```

Expected: the page shows `Stale Telegram form`.
What is happening: conflict detection blocked an overwrite.
Why this matters: two admins cannot silently replace each other's changes.

Issue a link token.

```text
Action: Issue link token
```

Expected: a raw token appears once.
Expected: future token lists show only a fingerprint.
What is happening: the channel service issued a one-time token.
Why this matters: the token can be copied for local linking without being
persisted as a secret.

Refresh the page.

```text
Expected token display: fingerprint only
```

Expected: the raw token is gone.
What is happening: persisted token audit rows are redacted.
Why this matters: screenshot evidence remains safe.

Validate webhook.

```text
Action: Validate webhook
```

Expected: a diagnostic row appears.
Expected: the diagnostic is local-only.
What is happening: the console records readiness evidence without contacting
Telegram.
Why this matters: QA must not have external side effects.

Review identities.

```text
Expected identifiers: masked
```

Expected: Telegram user and chat ids are masked.
What is happening: identity summaries are redacted before display.
Why this matters: administrators do not need private chat data.

Check cross-tenant denial.

```text
Principal: tenant-admin-globex
Target: Acme tenant query
```

Expected: access is denied.
What is happening: tenant scope is enforced before data rendering.
Why this matters: tenant isolation is a core platform requirement.

## Required Automated Evidence

Run Ruff.

```bash
uv run ruff check .
```

Expected: Ruff check passes.

Run formatting check.

```bash
uv run ruff format --check .
```

Expected: formatting check passes.

Run mypy.

```bash
uv run mypy src
```

Expected: mypy passes.

Run full coverage.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: coverage is at least 90 percent.

## UI Evidence Checklist

Expected: `01-local-login.png` shows Local Login.
Expected: `02-telegram-configuration-console-target.png` shows the console.
Expected: `03-telegram-configuration-console-direct-target.png` shows direct target.
Expected: screenshots contain no bot token.
Expected: screenshots contain no webhook secret.
Expected: screenshots contain no private message.
Expected: screenshots contain no raw prompt.
Expected: screenshots contain no run result.
Expected: screenshots contain no full Telegram id.
Expected: reviewer notes mention tenant scope.
Expected: reviewer notes mention redaction.
Expected: reviewer notes mention no external Telegram calls.

## Acceptance Notes Template

Reviewer:
Date:
Browser:
Principal used:
Tenant scope:
Screenshot folder:
Expected: login flow passed.
Expected: direct target flow passed.
Expected: tenant form flow passed.
Expected: stale conflict flow passed.
Expected: link token flow passed.
Expected: diagnostics flow passed.
What is happening: QA017 browser evidence is complete.
Why this matters: the feature can be reviewed without real Telegram secrets.

## Troubleshooting

If login is missing, check `LOCAL_PRINCIPAL_CATALOG_JSON`.
If the console is denied, check `telegram-config:read`.
If the save button is denied, check `telegram-config:write`.
If token actions are denied, check `telegram-config:tokens`.
If diagnostics are denied, check `telegram-config:diagnostics`.
If screenshots contain `local-dev-secret`, stop and file a redaction issue.
If screenshots contain a fake token value, stop and file a redaction issue.
If the browser cannot connect, restart the API.
If the database is empty, run migrations again.
If Playwright output is missing, inspect `output/playwright/qa017_ui`.

## Related Files

- `specs/017-telegram-configuration-console/qa017.md`
- `specs/017-telegram-configuration-console/qa017_user_guide.md`
- `specs/017-telegram-configuration-console/testing-instructions.md`
- `src/multi_agent_platform/api/routers/admin_telegram.py`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `tests/integration/api/test_admin_telegram_ui.py`
