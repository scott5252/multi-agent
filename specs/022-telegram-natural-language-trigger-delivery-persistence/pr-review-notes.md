# PR Review Notes: Telegram Natural-Language Trigger Delivery Persistence

## Review Focus

- Verify `telegram_command_aliases` and `telegram_update_receipts` are additive and tenant-scoped.
- Verify `notification_delivery_attempts.destination_fingerprint` is safe and nullable for existing data.
- Verify alias matching uses normalized exact matching, not fuzzy or model-based matching.
- Verify `/admin/telegram/api/aliases` and `/admin/telegram/aliases` enforce the same tenant authorization as existing Telegram configuration.
- Verify `/channels/telegram/webhook/{secret}` replays duplicate updates from persistent receipts before creating runs.
- Verify `/link` consumes persisted token audits and writes persistent identity links.
- Verify revoked identity summaries cause runtime alias denial.
- Verify disabled tenant Telegram configuration prevents alias-triggered runs.
- Verify local QA uses `MockTelegramBotApiClient` and does not call the live Bot API.
- Verify delivery attempts contain safe fingerprints and provider correlation refs only.

## Security Notes

- Bot token use remains behind `TELEGRAM_PROVIDER_TOKEN_REF`.
- Admin pages show safe labels, fingerprints, and masked identifiers.
- Delivery text is bounded and sanitized before send and before fingerprinting.
- The feature does not add fuzzy natural-language routing or model interpretation.

## Suggested Review Commands

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

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
