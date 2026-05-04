# QA022 UI: Telegram Natural-Language Trigger Delivery Persistence

## Goal

Guide a non-developer reviewer through the browser checks for Telegram command
alias configuration, masked link-token and identity evidence, tenant isolation,
and redaction-safe diagnostics on the `/admin/telegram` page.

## How To Use This Guide

Use this UI guide after copying `.env.qa022` and applying migrations. Keep the
API running while you review the browser. Save screenshots or reviewer notes
under `/tmp/qa022-*` so the evidence can be attached to a review record.

## Environment Setup

Copy the environment file:

```bash
cp specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022 .env
```

Expected: the local app uses `multi_agent_platform_qa022`, local-principal
auth, fake static Telegram secret references, and `.data/qa022-artifacts`.

Install dependencies and prepare the database:

```bash
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa022 && createdb -U postgres multi_agent_platform_qa022'
uv run alembic upgrade head
```

Expected: migrations finish, including `0019_telegram_alias_delivery`.

Seed tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa022 <<'SQL'
INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at)
VALUES
  ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO NOTHING;
SQL
```

Expected: Acme and Globex exist for tenant-scope switching.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the app serves `http://127.0.0.1:8000`.

Optional health check:

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
```

Expected: both commands exit successfully.

## Browser Walkthrough

### 1. Open Local Login

URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram`

Action:
Open the URL in a browser and look for `Local Login`.

Expected: principal cards are visible, including `tenant-admin-acme` and
`tenant-admin-globex`.

What is happening: the local-principal test mode is offering deterministic
review identities without Auth0.

Why this matters: QA can test tenant authorization and admin permissions
without external identity providers.

Evidence: save a screenshot as `/tmp/qa022-01-local-login.png`.

### 2. Sign In As Acme Tenant Admin

Action:
Select `tenant-admin-acme`.

Expected: the browser lands on `/admin/telegram` and the page title reads
`Telegram Configuration`.

What is happening: the admin shell wraps the Telegram configuration page using
the Acme tenant context.

Why this matters: all alias rows, link tokens, identities, and diagnostics must
be scoped to Acme.

Evidence: save `/tmp/qa022-02-acme-telegram-page.png`.

### 3. Review Provider Readiness

Action:
Look at the summary tiles at the top of the page.

Expected: the provider readiness tile is ready or clearly shows safe reference
labels, and token reference and webhook secret fields do not show raw values.

What is happening: the UI renders safe labels such as `static:***` instead of
actual secret values.

Why this matters: secret hygiene must hold before aliases or deliveries are
trusted.

### 4. Enable Tenant Telegram

Action:
In `Tenant Enablement`, check `Enabled`, keep `/run` and `/status` checked,
enter `QA022 ready`, then choose `Save`.

Expected: the page redirects back to `/admin/telegram?tenant_id=...` and the
enabled commands line includes `/run` and `/status`.

What is happening: the tenant configuration revision is updated through the
server-rendered form.

Why this matters: runtime alias routing must stop when tenant Telegram is not
enabled.

Evidence: note the visible status in `/tmp/qa022-ui-notes.txt`.

### 5. Confirm Alias Section

Action:
Find the section titled `Telegram Command Aliases`.

Expected: the section contains fields for alias text, published workflow
version, description, protected, enabled, and a `Save alias` button.

What is happening: the existing Telegram admin page now includes tenant alias
management without leaving the Telegram console.

Why this matters: non-developer tenant admins can bind natural-language
messages to published workflow versions from the browser.

### 6. Create Morning Briefing Alias

Action:
Use these values in the alias form:

- Alias: `Morning briefing`
- Published workflow version:
  `22222222-2222-2222-2222-222222222222`
- Description: `Daily Intelligence Briefing`
- Protected: checked
- Enabled: checked

Expected: after saving, the alias table includes `Morning briefing`,
`22222222-2222-2222-2222-222222222222`, `Linked identities required`, and
`enabled`.

What is happening: the form creates a tenant-scoped alias with exact normalized
matching.

Why this matters: this is the configuration that lets the Telegram webhook
route `Morning briefing` to the published Daily Intelligence Briefing workflow.

Evidence: save `/tmp/qa022-03-command-aliases.png`.

### 7. Issue A Link Token

Action:
In `Validation And Tokens`, choose `Issue link token`.

Expected: the page shows `One-Time Link Token` once and says future views show
only a fingerprint.

What is happening: the raw token is available only in the issuing response.

Why this matters: users can link Telegram while the admin console avoids
persisting or repeatedly rendering raw token values.

Evidence: save a reviewer note that the raw token appeared only once.

### 8. Refresh Token List

Action:
Reload `/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111`.

Expected: the raw token is gone and the `Link Tokens` table shows a short
fingerprint and status.

What is happening: the admin page is now reading persisted token audit records.

Why this matters: reviewers should see durable evidence without a reusable
secret.

### 9. Validate Webhook Readiness

Action:
Choose `Validate webhook`.

Expected: the `Diagnostics` table gains a webhook validation row with safe
status and no raw secret values.

What is happening: the app records a local validation-only diagnostic.

Why this matters: operators need safe readiness evidence before relying on
Telegram commands.

Evidence: save `/tmp/qa022-04-diagnostics.png`.

### 10. Switch To Globex

URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram`

Action:
Sign in as `tenant-admin-globex`, then open
`http://127.0.0.1:8000/admin/telegram?tenant_id=22222222-2222-2222-2222-222222222222`.

Expected: the Globex view does not show the Acme `Morning briefing` alias or
Acme link-token fingerprints.

What is happening: the same UI is rendered under a different tenant scope.

Why this matters: tenant alias and identity data must not bleed across
organizations.

Evidence: save `/tmp/qa022-05-globex-isolation.png`.

### 11. Cross-Tenant Denial From Browser Context

Action:
While signed in as `tenant-admin-globex`, open
`http://127.0.0.1:8000/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111`.

Expected: the page is denied or does not render Acme data.

What is happening: the server validates requested tenant scope against the
principal.

Why this matters: browser query parameters cannot be trusted for tenant access.

### 12. Redaction Review

Action:
Review all screenshots and visible tables.

Expected: screenshots do not contain `qa022-fake-token`, `local-dev-secret`,
full user id `987654321`, full chat id `123456789`, prompt bodies, or raw run
payloads.

What is happening: the UI intentionally shows safe references, fingerprints,
masked identifiers, and categories.

Why this matters: the Telegram feature handles credentials and private channel
data.

## Required Automated Evidence

Run focused UI and API tests:

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_telegram_ui.py \
  tests/integration/api/test_admin_telegram_api.py \
  tests/integration/api/test_telegram_webhook.py
```

Expected: all focused UI and webhook integration tests pass.

Run static checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Expected: Ruff and mypy pass.

Run the full coverage gate:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: full coverage is at least 90 percent.

Run Playwright validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/022-telegram-natural-language-trigger-delivery-persistence/validation.yml --start-processes
```

Expected: screenshots are written under `output/playwright/qa022_ui`.

## UI Evidence Checklist

- `/tmp/qa022-01-local-login.png` shows local login.
- `/tmp/qa022-02-acme-telegram-page.png` shows Acme Telegram configuration.
- `/tmp/qa022-03-command-aliases.png` shows `Telegram Command Aliases`.
- `/tmp/qa022-04-diagnostics.png` shows safe diagnostics.
- `/tmp/qa022-05-globex-isolation.png` shows Globex isolation.
- `/tmp/qa022-ui-notes.txt` records tenant enablement and link-token behavior.
- Screenshots contain no raw bot token.
- Screenshots contain no webhook secret.
- Screenshots contain no raw link token after refresh.
- Screenshots contain no full Telegram user id.
- Screenshots contain no full Telegram chat id.
- Screenshots contain no cross-tenant Acme data in the Globex view.

## Acceptance Notes Template

- Reviewer:
- Date:
- Browser:
- Acme login verified:
- Tenant enablement verified:
- Alias creation verified:
- One-time link token behavior verified:
- Diagnostics verified:
- Globex isolation verified:
- Redaction scan completed:
- Focused UI tests:
- Playwright output directory:
- Notes:

## Troubleshooting

- If login cards do not appear, confirm `.env.qa022` is copied to `.env`.
- If `tenant-admin-acme` is missing, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.
- If `/admin/telegram` is denied, confirm the principal has Telegram config
  permissions.
- If the alias section is missing, confirm the server is running the current
  branch.
- If alias save fails, confirm the workflow version value is a valid UUID.
- If stale alias errors appear, refresh the page and submit the current form.
- If link token issue fails, confirm `telegram-config:tokens` permission.
- If webhook validation shows not ready, confirm fake static Telegram secret
  references in `.env.qa022`.
- If screenshots show forbidden values, stop review and attach the screenshot
  path to the defect.
- If Playwright cannot reach the page, confirm the API is on
  `http://127.0.0.1:8000`.

## Related Files

- `specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022_user_guide.md`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `src/multi_agent_platform/api/routers/admin_telegram.py`
- `src/multi_agent_platform/api/ui/telegram_config.py`
- `tests/integration/api/test_admin_telegram_ui.py`
- `tests/integration/api/test_telegram_webhook.py`
