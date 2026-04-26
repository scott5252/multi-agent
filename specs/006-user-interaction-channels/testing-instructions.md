# Testing Instructions: User Interaction Channels

Run the local stack with `AUTH_MODE=local_principal`, apply migrations with
`uv run alembic upgrade head`, then start FastAPI and the worker:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
uv run python -m multi_agent_platform.workers.main
```

## Web API

1. `POST /runs` with `X-Idempotency-Key` and verify a `202` response with
   `run_id`, `state`, `status_url`, and `trace_id`.
2. Repeat the same request and verify the same `run_id`.
3. Reuse the key with different input and verify `idempotency_conflict`.
4. Call status, timeline, SSE events, result, subscription, callback,
   approval, cancel, artifact list, and artifact download URL endpoints.

## Web UI

1. Open `/runs`.
2. Submit the start form and confirm redirect to `/runs/{run_id}`.
3. Confirm run id, lifecycle state, timeline, result, notification state,
   artifacts, and support trace id are visible.
4. For a waiting run, submit approve, reject, resume, or cancel and confirm
   stale controls are rejected after the first accepted decision.

## Telegram

1. Create a link token with `POST /channels/telegram/link-token`.
2. Send `/link <token>` to `/channels/telegram/webhook/{secret}`.
3. Verify `/run`, `/status`, `/result`, `/artifacts`, `/subscribe`, `/approve`,
   `/reject`, `/resume`, and `/cancel` after linking.
4. Send a duplicate `update_id` and verify the stored outcome is returned.
5. Send a protected command from an unlinked chat and verify `unauthorized`.

## Review Gates

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Reviewers should verify Web UI, Telegram, and Web API flows, live or persisted
progress, terminal notifications, final result retrieval, approval/resume,
cancellation, artifact downloads, auth denials, rate limits, and cross-channel
recovery.

