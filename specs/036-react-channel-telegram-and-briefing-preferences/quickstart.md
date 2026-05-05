# Quickstart: React Channel, Telegram, And Briefing Preferences

## Scope

Spec 036 adds a React workspace at `/admin/app/channels` for channel readiness, Telegram configuration, aliases, delivery diagnostics, safe run status links, and Daily Intelligence Briefing preference profiles. Existing Jinja routes for Telegram, briefing preferences, and channel run UI remain available as fallbacks.

## Local Setup

```bash
uv sync
uv run alembic upgrade head
cd frontend/admin
npm install
npm run typecheck
npm run test
npm run build
```

## Focused Backend Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py \
  tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py \
  tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

## Generated Types And Static Checks

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run mypy src
uv run ruff check .
uv run ruff format --check .
```

## QA Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/036-react-channel-telegram-and-briefing-preferences

uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml

uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml \
  --start-processes
```

## Manual Reviewer Walkthrough

1. Copy `.env.qa036` after implementation.
2. Start the FastAPI app and worker.
3. Sign in as `platform-admin`.
4. Open `/admin/app/channels`.
5. Confirm readiness cards, Telegram enablement, webhook validation, identities, aliases, delivery diagnostics, safe run links, and admin-safe preference summaries render without unsafe values.
6. Sign in as `tenant-admin-acme`.
7. Confirm Acme aliases, link-token creation, delivery diagnostics, and safe preference summaries render without Globex data.
8. Sign in as `tenant-user-acme`.
9. Confirm the user can edit only their own Daily Briefing preference profile.
10. Confirm scheduled briefing time is labeled as profile metadata.
11. Confirm link-token value appears only immediately after creation.

## Redaction Scan

```bash
rg -n "qa036-secret-value|bot token|webhook secret|full telegram|link token after creation|private message|raw preference|raw prompt|run result|raw tool payload|/Users/|unauthorized tenant label" \
  /tmp/qa036-* output/playwright/qa036_ui || true
```

Any match outside intentional documentation text is a blocker.
