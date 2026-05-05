# QA036 User Guide: Spec 036 - React Channel, Telegram, And Briefing Preferences

## Detailed Overview

QA036 adds a React workspace for the operational pieces around Telegram-driven workflows and Daily Intelligence Briefing preferences.

The workspace lives at `/admin/app/channels`.

It is meant for three kinds of users.

Platform administrators can review channel and Telegram readiness across authorized tenants.

Tenant administrators can manage their own tenant's Telegram configuration, natural-language aliases, one-time identity link codes, masked linked identities, delivery diagnostics, safe run links, and redacted preference summaries.

Tenant users can manage their own Daily Intelligence Briefing preference profile and open safe run status links.

The most important safety promise is simple: the screen should be useful without revealing sensitive data.

Reviewers should never see real bot tokens.

Reviewers should never see webhook secrets.

Reviewers should never see full Telegram user ids or chat ids.

Reviewers should never see private Telegram messages.

Reviewers should never see raw preference values in administrator summaries.

Reviewers should never see raw prompts, completions, run results, or external tool payloads.

Reviewers should never see another tenant's data by changing browser URLs.

One-time link codes are special. The system may show the code only immediately after it is created. After the page refreshes, QA evidence and screenshots should show only masked status, expiration, consumption state, and audit reference.

The local QA environment uses fake secret references and mocked Telegram delivery boundaries. It must not call real Telegram, Auth0, provider credentials, or external tools.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA036 behavior in a browser.

Use this guide if you are checking screenshots before a pull request is approved.

Use this guide if you are not planning to inspect Python, TypeScript, or database implementation details.

Use `qa036.md` if you need exact curl commands and automated evidence.

Use `qa036_ui.md` if you need a longer browser-first walkthrough.

Use this user guide as a plain-language checklist.

## Manual QA Prerequisites

Start from the repository root.

Copy the QA036 environment file.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036 .env
uv sync
```

Build the React admin assets.

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Start PostgreSQL and reset the QA036 database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa036 && createdb -U postgres multi_agent_platform_qa036'
uv run alembic upgrade head
mkdir -p .data/qa036-artifacts output/playwright/qa036_ui
```

Seed the two deterministic tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa036 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Start the API in one terminal.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected result: `http://127.0.0.1:8000/health/live` returns a healthy response.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login`.

2. Choose `platform-admin`.

3. Open `http://127.0.0.1:8000/admin/app/channels`.

4. Confirm the page title says `Channel, Telegram, and Briefing Preferences`.

5. Confirm platform view includes Acme and Globex readiness summaries.

6. Confirm reference labels are safe phrases such as `Telegram provider ref ready`.

7. Confirm no token, secret, full Telegram id, private message, raw prompt, or raw result appears.

8. Click `Validate Acme` if visible.

9. Confirm the validation result says it used local mock-safe evidence.

10. Find the alias table.

11. Confirm `Morning briefing` is visible.

12. Click `Create Alias`.

13. Confirm the result shows accepted status and audit evidence.

14. Review linked identities.

15. Confirm the Telegram user and chat labels are masked.

16. Review delivery diagnostics.

17. Confirm delivery rows show status, retry category, Bot API boundary status, trace reference, and audit reference.

18. Click `Open Run Status`.

19. Confirm the safe run status page shows `Daily briefing workflow`.

20. Confirm the run status page shows next step, artifact reference, and audit reference.

21. Confirm the run status page does not show raw run inputs, prompts, completions, messages, or run results.

22. Return to `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`.

23. Choose `tenant-admin-acme`.

24. Confirm the page is Acme-scoped.

25. Search visually for `Globex`.

26. Confirm Globex is not visible to the Acme tenant admin.

27. Review Acme alias, identity, delivery, and preference admin sections.

28. Click `Import`.

29. Confirm the preference import result shows safe artifact metadata and row or field count.

30. Click `Export`.

31. Confirm the preference export result shows safe artifact metadata and audit evidence.

32. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111`.

33. Choose `tenant-user-acme`.

34. Confirm the preference profile panel is visible.

35. Confirm alias administration controls are not visible to the tenant user.

36. Click `Save Preferences`.

37. Confirm the result reports saved preference profile, revision evidence, and runtime readiness.

38. Confirm scheduled time is shown as profile preference evidence, not as a guaranteed scheduler.

39. Optional: sign back in as tenant admin and click `Create Code`.

40. If the code appears, do not screenshot it.

41. Refresh the page.

42. Confirm the link-token area now shows masked status only.

43. Capture screenshots only after the token is masked.

44. Open a private or signed-out browser and try `/admin/app/channels`.

45. Confirm the workspace is denied before login.

46. Record all screenshots and notes under `output/playwright/qa036_ui` or `/tmp/qa036-ui-*`.

## Expected Results

Expected: platform admin sees authorized tenant readiness for Acme and Globex.

Expected: tenant-admin-acme sees Acme only.

Expected: tenant-user-acme sees their own preference profile and safe run status access.

Expected: unauthenticated users are denied.

Expected: Telegram configuration uses safe reference labels, not raw secret values.

Expected: webhook validation is explicit and mock-safe.

Expected: alias actions return accepted, validation, replay, conflict, or denied states with audit evidence.

Expected: linked Telegram identities are masked.

Expected: delivery diagnostics are bounded.

Expected: safe run status omits raw run content.

Expected: preference admin summaries are redacted.

Expected: import and export actions show artifact metadata only.

Expected: one-time link codes are not captured in screenshots or saved JSON evidence.

Expected: Globex never appears in Acme tenant-admin evidence.

Expected: no local filesystem paths appear in saved QA evidence.

## Evidence To Capture

Capture a screenshot of the platform admin dashboard.

Capture a screenshot of webhook validation result.

Capture a screenshot of alias management result.

Capture a screenshot of masked linked identities.

Capture a screenshot of delivery diagnostics.

Capture a screenshot of safe run status.

Capture a screenshot of Acme tenant-admin dashboard.

Capture a screenshot of Acme tenant-user preference profile.

Capture a screenshot of preference import/export result.

Create `/tmp/qa036-ui-redaction-review.md` with a short statement that no unsafe values appeared in screenshots.

Create `/tmp/qa036-ui-token-review.md` if the one-time code was tested. State that the code was visible once and not captured.

Keep `/tmp/qa036-*` JSON evidence from `qa036.md` if the API guide is also run.

## Security And Redaction Checks

Check screenshots for fake secret values.

Check screenshots for phrases that look like bot tokens.

Check screenshots for webhook secret values.

Check screenshots for full Telegram identifiers.

Check screenshots for one-time token values after creation.

Check screenshots for private messages.

Check screenshots for raw preference values in admin summaries.

Check screenshots for raw prompts or completions.

Check screenshots for run results.

Check screenshots for raw tool payloads.

Check screenshots for local filesystem paths.

Check screenshots for unauthorized tenant labels.

Run the text scan after automated evidence is captured.

```bash
! rg -n "qa036-secret-value|bot token|webhook secret|full telegram|pair-code|private message|raw preference|raw prompt|run result|raw tool payload|/Users/|unauthorized tenant label" /tmp/qa036-* output/playwright/qa036_ui
```

Expected result: the scan exits 0.

## Tenant Isolation Checks

Sign in as `platform-admin` and confirm Acme and Globex can be reviewed intentionally.

Sign in as `tenant-admin-acme` and confirm Acme appears.

Sign in as `tenant-admin-acme` and confirm Globex does not appear.

Sign in as `tenant-user-acme` and confirm tenant admin alias controls are not visible.

Try to open the Globex tenant id while signed in as `tenant-admin-acme`.

Expected result: cross-tenant access is denied.

Try to open the channel workspace while signed out.

Expected result: unauthenticated access is denied.

## Automated Checks For Reviewers

Run focused backend checks.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
```

Run frontend checks.

```bash
cd frontend/admin && npm run typecheck && npm run test && npm run build && cd ../..
```

Run required project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run full Spec QA.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml
```

Run browser QA.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml --start-processes
```

## Troubleshooting

If the login page is missing, confirm `.env.qa036` is copied to `.env`.

If the page says React admin is unavailable, rebuild frontend assets.

If Acme tenant rows are missing, rerun the seed SQL command.

If a cross-tenant check returns 200, stop and investigate before approving.

If a one-time code appears in a screenshot, delete that screenshot and retake it after refresh.

If Playwright fails to click a button, verify the current principal has the right role.

If redaction scan fails, inspect the exact file and remove unsafe evidence before rerunning.

If quality commands fail outside QA036 files, check whether the failure belongs to unrelated local work before changing it.

