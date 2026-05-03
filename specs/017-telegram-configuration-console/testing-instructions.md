# Testing Instructions: Telegram Configuration Console

## Focused Test Command

```bash
uv run pytest --no-cov \
  tests/unit/admin/telegram_config \
  tests/unit/api/test_telegram_config_schemas.py \
  tests/unit/auth/test_telegram_config_policy.py \
  tests/unit/db/test_telegram_config_repository.py \
  tests/contract/test_telegram_configuration_contract.py \
  tests/integration/db/test_telegram_config_migration.py \
  tests/integration/api/test_admin_telegram_api.py \
  tests/integration/api/test_admin_telegram_ui.py \
  tests/docs/test_telegram_configuration_docs.py
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual API Review

1. Copy `specs/017-telegram-configuration-console/.env.qa017` to `.env`.
2. Start PostgreSQL and run migrations.
3. Start the API.
4. Call `/admin/telegram/api/readiness` as `platform-admin`.
5. Call `/admin/telegram/api/config` as `tenant-admin-acme`.
6. Attempt Acme config as `tenant-admin-globex` and expect `403`.
7. Issue a link token as `tenant-admin-acme`.
8. Simulate `/link <token>` through `/channels/telegram/webhook/local-dev-secret`.
9. Confirm `/admin/telegram/api/identities` masks Telegram ids.
10. Confirm `/admin/telegram/api/diagnostics` contains safe categories only.

## Manual Browser Review

1. Open `/auth/local-login?redirect_to=/admin/telegram`.
2. Sign in as `platform-admin`.
3. Confirm the page renders under the admin shell.
4. Select Acme tenant scope.
5. Enable Telegram and save protected commands.
6. Submit a stale form revision and verify the conflict.
7. Issue and revoke a link token.
8. Revoke a linked identity if present.
9. Validate the webhook.
10. Capture screenshots and search them for forbidden values.

## Forbidden Values

The following must not appear in rendered admin UI, diagnostics, screenshots, or
audit-safe metadata:

- real bot tokens
- webhook secret values
- private Telegram messages
- raw prompts
- run results
- full Telegram user ids
- full Telegram chat ids
- unauthorized tenant data
