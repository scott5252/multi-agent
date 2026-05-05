# QA036 UI: React Channel, Telegram, And Briefing Preferences

## Goal

Validate the browser experience for the QA036 React channel workspace at `/admin/app/channels` and the safe run status page at `/admin/app/channels/runs/qa036-run-morning-briefing`.

The reviewer should confirm that platform admins, tenant admins, and tenant users see the right controls, tenant scope, safe readiness summaries, masked Telegram identity labels, redacted preference summaries, and no raw secret or private content.

## How To Use This Guide

Use this walkthrough after copying `.env.qa036` and starting the local app.

Capture screenshots into `output/playwright/qa036_ui` or use reviewer note files named `/tmp/qa036-ui-*.md`.

Do not capture screenshots while a newly created one-time link token is visibly displayed. If you click `Create Code`, refresh the page before screenshot capture so only masked token status remains.

Expected: the reviewer can follow this UI guide without reading the backend QA guide first.

## Environment Setup

Copy the QA036 environment and build assets.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036 .env
uv sync
cd frontend/admin && npm install && npm run build && cd ../..
```

Expected: dependencies install and React assets build successfully.

Start the database and migrate.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa036 && createdb -U postgres multi_agent_platform_qa036'
uv run alembic upgrade head
mkdir -p .data/qa036-artifacts output/playwright/qa036_ui
```

Expected: only the QA036 database is reset.

Seed the tenant rows.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa036 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist for scope selection and tenant isolation checks.

Start the API and worker.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: `http://127.0.0.1:8000/health/live` returns 200.

Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected: the local principal chooser is visible.

## Browser Walkthrough

1. Start unauthenticated.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: open the URL in a clean browser profile or after clearing the local principal cookie.

Expected: the page is denied or redirects to a safe login path instead of rendering the workspace.

What is happening: the protected React shell requires an authenticated principal before it serves channel readiness.

Why this matters: channel readiness, Telegram aliases, linked identities, and briefing profiles are tenant-scoped operational data.

Evidence: save `/tmp/qa036-ui-unauthenticated.md` with the observed status, or capture `qa036-react-channels-denied.png`.

2. Sign in as `platform-admin`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels`

Action: choose `platform-admin`.

Expected: the browser lands on `/admin/app/channels` and the React shell loads.

What is happening: the local-principal cookie is set and the shell requests `/admin/app/channels/shell.json`.

Why this matters: platform access must work in local-principal mode and match Auth0-shaped route tests.

Evidence: capture `qa036-react-channels-platform.png`.

3. Review the platform readiness header.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: inspect the page title, scope label, update timestamp, and `Refresh` button.

Expected: title reads `Channel, Telegram, and Briefing Preferences`, scope is platform or all authorized scopes, and refresh does not change tenant isolation.

What is happening: React renders a backend-owned `ChannelTelegramBriefingDashboard`.

Why this matters: the browser should not infer readiness or tenant access rules by itself.

Evidence: note the timestamp and active scope in `/tmp/qa036-ui-platform-header.md`.

4. Review readiness cards.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: scan the Telegram, webhook, secret-reference, identity, delivery, and preference resolver cards.

Expected: Acme and Globex readiness appears for platform admin, with safe labels such as `Telegram provider ref ready`.

What is happening: the cards summarize deterministic readiness fixtures and safe remediation guidance.

Why this matters: administrators need a fast readiness view without token, webhook secret, private message, or raw identifier leakage.

Evidence: capture a screenshot that shows cards but no unsafe values.

5. Review Telegram configuration.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: find the Telegram tenant configuration panel and inspect the `Save` action.

Expected: the panel shows enabled state, safe reference labels, revision, last validation timestamp, and audit reference.

What is happening: the panel displays safe reference summaries, not actual secret values.

Why this matters: token and webhook-signing values must remain in the secret provider, not the browser.

Evidence: write `/tmp/qa036-ui-config-panel.md` with the visible labels.

6. Validate webhook readiness.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: click `Validate Acme` if visible.

Expected: the result says webhook validation completed with local mock-safe evidence.

What is happening: the browser posts to `/admin/app/channels/telegram/webhook/validate`.

Why this matters: readiness refresh must be explicit, audited, idempotent, and safe in local QA.

Evidence: capture `qa036-react-channels-webhook.png` after the result appears.

7. Review alias management.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: find `Morning briefing`, protected readiness, lifecycle status, and alias action buttons.

Expected: `Morning briefing` is visible, actions include `Refresh`, and audit evidence is shown.

What is happening: aliases are tenant-scoped natural-language triggers that map to the Daily Briefing workflow.

Why this matters: alias changes are operationally sensitive and must show validation, revision, idempotency, and audit context.

Evidence: note the alias id and audit reference in `/tmp/qa036-ui-alias.md`.

8. Create alias evidence.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: click `Create Alias`.

Expected: the mutation result reports accepted status and protected readiness.

What is happening: the form uses a deterministic safe alias payload for `Morning briefing`.

Why this matters: tenant admins need a repeatable alias workflow that does not depend on live Telegram.

Evidence: capture `qa036-react-channels-alias.png`.

9. Review linked identities and link-token masked state.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: inspect the linked identity panel.

Expected: Telegram identity labels look masked, such as `Telegram user tg-***-1842` and `Chat chat-***-9081`.

What is happening: the backend provides masked identity summaries only.

Why this matters: full Telegram user ids and chat ids are private and must not be visible.

Evidence: capture `qa036-react-channels-identities.png`.

10. Optional link-token creation.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: click `Create Code` only if the reviewer is ready to observe the one-time display. Do not screenshot the visible code.

Expected: the token appears once with expiration guidance. After refresh, only masked token status remains.

What is happening: the browser receives the immediate creation result, then later dashboard loads are masked.

Why this matters: SC-003 requires one-time visibility and no retained token evidence.

Evidence: write a reviewer note that the code was visible once, then refresh and capture the masked state only.

11. Review delivery diagnostics.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: inspect delivery status, retry category, Bot API boundary status, trace reference, and audit reference.

Expected: the attempt shows safe status such as `delivered`, retry category `none`, and boundary status `mocked`.

What is happening: the UI renders bounded recent delivery attempt summaries.

Why this matters: support staff need delivery evidence without private Telegram message content.

Evidence: capture `qa036-react-channels-delivery.png`.

12. Open safe run status.

Page URL: `http://127.0.0.1:8000/admin/app/channels`

Action: click `Open Run Status`.

Expected: the browser opens `/admin/app/channels/runs/qa036-run-morning-briefing` and shows `Daily briefing workflow`, status, next step, artifacts, and audit reference.

What is happening: React loads `/admin/app/channels/runs/qa036-run-morning-briefing/status.json`.

Why this matters: user-facing run links must not expose raw run inspection, prompts, completions, or run results.

Evidence: capture `qa036-react-channels-run-status.png`.

13. Switch to `tenant-admin-acme`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-admin-acme`.

Expected: the page shows Acme readiness, aliases, identities, diagnostics, and safe preference summaries.

What is happening: the active scope is Acme and the bootstrap URL carries the Acme tenant id.

Why this matters: tenant admins must see their own tenant only.

Evidence: capture `qa036-react-channels-tenant-admin.png`.

14. Check that Globex is absent for Acme tenant admin.

Page URL: `http://127.0.0.1:8000/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`

Action: search the page for `Globex`.

Expected: `Globex` is not visible.

What is happening: the backend filters readiness, allowed scope options, aliases, identities, diagnostics, and preferences.

Why this matters: UI filtering alone is not enough; the JSON payload itself must be tenant-scoped.

Evidence: note the search result in `/tmp/qa036-ui-tenant-isolation.md`.

15. Switch to `tenant-user-acme`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-user-acme`.

Expected: the user sees their briefing preference panel and not the alias administration table.

What is happening: tenant users are allowed into the channel workspace for preferences and safe run status, not tenant-wide Telegram administration.

Why this matters: preference profile management is user-facing, while alias and tenant configuration remain administrator workflows.

Evidence: capture `qa036-react-channels-tenant-user.png`.

16. Save briefing preferences.

Page URL: `http://127.0.0.1:8000/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`

Action: click `Save Preferences`.

Expected: the result says the preference profile was saved with redacted summaries and a new revision.

What is happening: React posts safe summarized fields for timezone, location, topics, VIP hints, workday hours, commute mode, account refs, output style, and scheduled time.

Why this matters: preference saves need revision evidence and runtime readiness while keeping raw private values out of admin summaries.

Evidence: capture `qa036-react-channels-preference-save.png`.

17. Review admin preference summaries.

Page URL: sign back in as `tenant-admin-acme` and open `/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`

Action: inspect the preference admin panel and click `Import` and `Export`.

Expected: summaries show safe counts, masked hints, artifact references, row counts, revision metadata, and audit references.

What is happening: import/export actions return artifact metadata, not raw preference content.

Why this matters: administrators can support users without seeing private location details, VIP sender values, account identifiers, or raw preference payloads.

Evidence: capture `qa036-react-channels-preference-admin.png`.

18. Final visual redaction review.

Page URL: all QA036 screenshots.

Action: review each screenshot and note whether any unsafe value appears.

Expected: screenshots omit real bot tokens, webhook secrets, full Telegram ids, one-time token values after creation, private messages, raw preference values, raw prompts, run results, local filesystem paths, and unauthorized tenant labels.

What is happening: this is the human visual companion to the automated text scan.

Why this matters: images can reveal issues that text scans cannot parse.

Evidence: record the final result in `/tmp/qa036-ui-redaction-review.md`.

## Required Automated Evidence

Run QA document validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/036-react-channel-telegram-and-briefing-preferences
```

Expected: QA036 guide, UI guide, and environment file pass validation.

Run focused QA036 tests.

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py \
  tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py \
  tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Expected: focused backend tests pass.

Run frontend evidence checks.

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Expected: TypeScript, Vitest, and Vite build pass.

Run project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: repository quality gates pass.

Run Playwright UI validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml --start-processes
```

Expected: Playwright writes screenshots into `output/playwright/qa036_ui`.

Run screenshot-sidecar text scan.

```bash
! rg -n "qa036-secret-value|bot token|webhook secret|full telegram|pair-code|private message|raw preference|raw prompt|run result|raw tool payload|/Users/|unauthorized tenant label" output/playwright/qa036_ui
```

Expected: no unsafe text appears in Playwright output metadata.

## UI Evidence Checklist

- `qa036-react-channels-denied.png` shows protected access before login.
- `qa036-react-channels-platform.png` shows platform readiness.
- `qa036-react-channels-webhook.png` shows validation result.
- `qa036-react-channels-alias.png` shows alias action result.
- `qa036-react-channels-identities.png` shows masked Telegram identities.
- `qa036-react-channels-delivery.png` shows bounded delivery diagnostics.
- `qa036-react-channels-run-status.png` shows safe run status.
- `qa036-react-channels-tenant-admin.png` shows Acme tenant admin scope.
- `qa036-react-channels-tenant-user.png` shows preference profile access.
- `qa036-react-channels-preference-admin.png` shows redacted summaries and import/export metadata.
- `/tmp/qa036-ui-redaction-review.md` records the final human visual scan.

Expected: every screenshot has a reviewer note and no screenshot captures a visible one-time token.

## Acceptance Notes Template

- Reviewer:
- Date:
- Browser:
- Platform admin login passed:
- Tenant admin login passed:
- Tenant user login passed:
- Globex hidden from Acme:
- Link token visible once and not captured:
- Delivery diagnostics safe:
- Run status safe:
- Preference summaries redacted:
- Screenshots captured:
- Redaction notes:
- Follow-up issues:

Expected: the reviewer can paste this block into PR notes or QA signoff.

## Troubleshooting

- If `/auth/local-login` is not visible, confirm `.env.qa036` was copied to `.env`.
- If `/admin/app/channels` shows the generic shell only, rebuild React assets.
- If `Globex` appears while signed in as `tenant-admin-acme`, stop and investigate tenant scoping.
- If a one-time token appears in a screenshot, delete that screenshot and recapture after refresh.
- If the page shows `React admin unavailable`, inspect the browser network request for `/admin/app/channels/shell.json`.
- If buttons are missing, confirm the current principal has tenant admin or platform admin role codes.
- If the worker is noisy, check that `QA036_MOCK_BOT_API_DELIVERY=true`.
- If Playwright fails on login, rerun with a clean output directory and confirm the local login page is reachable.

## Related Files

- `specs/036-react-channel-telegram-and-briefing-preferences/qa036.md`
- `specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036`
- `specs/036-react-channel-telegram-and-briefing-preferences/qa036_user_guide.md`
- `specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml`
- `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`
- `frontend/admin/src/components/channelTelegramBriefing/RunStatusSummaryPage.tsx`
