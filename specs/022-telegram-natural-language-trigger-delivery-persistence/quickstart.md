# Quickstart: Telegram Natural-Language Trigger Delivery Persistence

## Local Setup

```bash
uv sync
cp specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa022 && createdb -U postgres multi_agent_platform_qa022'
uv run alembic upgrade head
```

Expected: migrations apply through `0019_telegram_alias_delivery`.

## Start Services

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

Expected: `/health/live`, `/health/ready`, `/version`, and `/dependencies` return success.

## Browser Alias Configuration

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram`.
2. Choose `tenant-admin-acme`.
3. Confirm the page contains `Telegram Command Aliases`.
4. Create alias `Morning briefing` for the QA published workflow version.
5. Confirm the alias appears with status `enabled` and protected identity policy.

Expected: no raw bot token, webhook secret, raw link token, full Telegram user ID, or full chat ID appears.

## API Alias Configuration

```bash
curl --fail --silent \
  -H 'X-Local-Principal: tenant-admin-acme' \
  -H 'Content-Type: application/json' \
  -X POST http://127.0.0.1:8000/admin/telegram/api/aliases \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "alias_text": "Morning briefing",
    "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
    "description": "Daily Intelligence Briefing",
    "protected": true,
    "enabled": true
  }'
```

Expected: response includes `alias_normalized` as `morning briefing` and excludes secret values.

## Telegram Link And Trigger

Issue a link token:

```bash
curl --fail --silent \
  -H 'X-Local-Principal: tenant-admin-acme' \
  -X POST 'http://127.0.0.1:8000/admin/telegram/api/link-tokens?tenant_id=11111111-1111-1111-1111-111111111111'
```

Send `/link <token>` to the webhook, then send `Morning briefing`:

```bash
curl --fail --silent \
  -H 'Content-Type: application/json' \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -d '{"update_id": 22001, "message": {"chat": {"id": 123456789}, "from": {"id": 987654321}, "text": "Morning briefing"}}'
```

Expected: a run is created once, the mock Bot API records a `sendMessage` request to chat `123456789`, and a delivery attempt is persisted with safe fingerprints.

## Duplicate Update Check

Repeat the same `update_id` request three times.

Expected: each duplicate returns the original response and no additional run or delivery attempt is created.

## Quality Commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/022-telegram-natural-language-trigger-delivery-persistence/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/022-telegram-natural-language-trigger-delivery-persistence/validation.yml --start-processes
```
