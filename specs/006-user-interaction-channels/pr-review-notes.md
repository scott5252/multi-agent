# PR Review Notes: User Interaction Channels

## Implementation Summary

- Added shared channel domain models, normalization, idempotency, state
  mapping, error categories, artifact grants, notifications, callbacks,
  Telegram command handling, and SSE helpers.
- Added user-facing Web API routes under `/runs`, Web UI run list/detail pages,
  Telegram webhook handling, and Telegram link-token issuance.
- Added channel SQLAlchemy models and Alembic revision
  `0006_user_interaction_channels` for sessions, links, normalized requests,
  idempotency records, timeline events, notifications, callback attempts,
  artifact grants, and audits.
- Added docs, QA guide, testing instructions, README guidance, and contract,
  unit, integration, docs, and performance tests.

## Review Focus

- Shared invocation behavior: all channels route through `ChannelService`.
- Lifecycle consistency: user-visible states are exactly `queued`, `running`,
  `waiting-for-input`, `completed`, `failed`, and `canceled`.
- Authorization behavior: Web UI/API reuse platform auth; Telegram requires a
  one-time link token before protected commands.
- Approval and resume flows: prompt version and action validation reject stale
  responses without mutating the run.
- Notification and callback behavior: terminal notifications and callbacks are
  evidence-producing side paths and never change run lifecycle.
- Artifact access: responses expose metadata and short-lived URLs only, never
  artifact bytes.
- Known risk: the initial runtime facade remains an in-process runtime service
  for local and test behavior; the channel persistence schema is ready for a
  later database-backed service implementation.

## Validation Evidence

Validation run on 2026-04-24:

- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed, 325 files already formatted.
- `uv run mypy src`: passed, no issues in 146 source files.
- Channel-focused suite:
  `uv run pytest --no-cov tests/unit/channels tests/unit/api/test_channel_run_schemas.py tests/unit/db/test_channel_models.py tests/unit/config/test_settings.py tests/contract/test_channel_layer_contract.py tests/integration/api/test_channel_run_api.py tests/integration/api/test_web_run_ui.py tests/integration/api/test_telegram_webhook.py tests/integration/channels tests/docs/test_user_interaction_channels_docs.py tests/performance/channels/test_channel_latency.py`
  passed, 42 tests.
- Full coverage suite:
  `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
  passed, 267 tests, total coverage 90.47%.
