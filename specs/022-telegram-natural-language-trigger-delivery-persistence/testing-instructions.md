# Testing Instructions: Telegram Natural-Language Trigger Delivery Persistence

## Focused Test Command

```bash
uv run pytest --no-cov \
  tests/unit/channels/test_telegram_delivery.py \
  tests/unit/db/test_telegram_config_repository.py \
  tests/unit/db/test_channel_models.py \
  tests/contract/test_telegram_alias_delivery_contract.py \
  tests/integration/api/test_admin_telegram_api.py \
  tests/integration/api/test_admin_telegram_ui.py \
  tests/integration/api/test_telegram_webhook.py
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual API Review

1. Copy `specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022` to `.env`.
2. Start PostgreSQL and run migrations through `0019_telegram_alias_delivery`.
3. Start the API and worker.
4. Call `/admin/telegram/api/config` as `tenant-admin-acme`.
5. Enable tenant Telegram configuration.
6. Create the `Morning briefing` alias with `/admin/telegram/api/aliases`.
7. Issue a link token with `/admin/telegram/api/link-tokens`.
8. Send `/link TOKEN` to `/channels/telegram/webhook/local-dev-secret`.
9. Send `Morning briefing` to the same webhook chat.
10. Repeat the same `update_id` and verify the response replays.
11. Query diagnostics and ensure only safe categories and masked values appear.
12. Disable tenant Telegram configuration and confirm the alias no longer starts a run.

## Manual Browser Review

1. Open `/auth/local-login?redirect_to=/admin/telegram`.
2. Sign in as `tenant-admin-acme`.
3. Confirm `Telegram Command Aliases` appears.
4. Create the `Morning briefing` alias.
5. Confirm the alias row shows linked identities required and enabled.
6. Issue a link token and confirm only the one-time page shows the raw token.
7. Refresh the page and confirm future views show only fingerprints.
8. Switch to `tenant-admin-globex` and confirm Acme aliases are not visible.
9. Validate the webhook readiness panel.
10. Capture screenshots and scan them for forbidden values.

## Forbidden Values

The following must not appear in rendered admin UI, diagnostics, screenshots, or
audit-safe metadata:

- real bot tokens
- webhook secret values
- raw link tokens outside the one-time issue response
- private Telegram messages
- raw prompts
- raw run results
- full Telegram user ids
- full Telegram chat ids
- unauthorized tenant data
