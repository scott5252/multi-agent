# Quickstart: User Interaction Channels

## Prerequisites

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Start PostgreSQL and apply migrations:

   ```bash
   uv run alembic upgrade head
   ```

3. Configure local auth and optional channel settings in `.env`:

   ```text
   AUTH_MODE=local
   TELEGRAM_WEBHOOK_SECRET=local-dev-secret
   CHANNEL_CALLBACK_SIGNING_SECRET_REF=env:CHANNEL_CALLBACK_SIGNING_SECRET
   CHANNEL_ARTIFACT_URL_TTL_SECONDS=300
   ```

## Run The API And Worker

Start FastAPI:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Start background workers for runtime and notification delivery:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Web API Smoke Test

1. Start a run through the user-facing channel facade:

   ```bash
   curl -X POST http://127.0.0.1:8000/runs \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: local-tenant" \
     -H "X-Idempotency-Key: demo-run-001" \
     -d '{
       "workflow_id": "published-demo-workflow",
       "inputs": {"topic": "channel smoke test"},
       "channel": "web_api"
     }'
   ```

2. Copy the returned `run_id`, then retrieve status:

   ```bash
   curl http://127.0.0.1:8000/runs/RUN_ID/status \
     -H "X-Tenant-ID: local-tenant"
   ```

3. Retrieve timeline events:

   ```bash
   curl "http://127.0.0.1:8000/runs/RUN_ID/timeline?limit=100" \
     -H "X-Tenant-ID: local-tenant"
   ```

4. Retrieve result after completion:

   ```bash
   curl http://127.0.0.1:8000/runs/RUN_ID/result \
     -H "X-Tenant-ID: local-tenant"
   ```

## Web UI Smoke Test

1. Open `http://127.0.0.1:8000/runs` in a browser.
2. Start or select a run.
3. Confirm the run details page shows the run id, state, progress summary,
   timeline, trace id, result area, artifact area, and notification
   subscription state.
4. While the run is active, confirm the page receives SSE updates or falls back
   to polling without losing the latest persisted status.
5. For a waiting run, approve, reject, resume, or cancel from the prompt panel
   and confirm stale buttons are disabled after the first accepted response.

## Telegram Webhook Smoke Test

1. Create a one-time link token while signed into the Web UI.
2. Simulate Telegram linking:

   ```bash
   curl -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
     -H "Content-Type: application/json" \
     -d '{
       "update_id": 1001,
       "message": {
         "message_id": 1,
         "chat": {"id": 12345, "type": "private"},
         "from": {"id": 67890, "is_bot": false, "first_name": "Local"},
         "text": "/link LINK_TOKEN"
       }
     }'
   ```

3. Simulate status retrieval:

   ```bash
   curl -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
     -H "Content-Type: application/json" \
     -d '{
       "update_id": 1002,
       "message": {
         "message_id": 2,
         "chat": {"id": 12345, "type": "private"},
         "from": {"id": 67890, "is_bot": false, "first_name": "Local"},
         "text": "/status RUN_ID"
       }
     }'
   ```

4. Verify duplicate `update_id` delivery returns the stored outcome and does
   not create a second action.

## Approval And Resume Validation

1. Start a workflow that enters `waiting-for-input`.
2. Retrieve status and confirm `waiting_prompt` is present:

   ```bash
   curl http://127.0.0.1:8000/runs/RUN_ID/status \
     -H "X-Tenant-ID: local-tenant"
   ```

3. Approve:

   ```bash
   curl -X POST http://127.0.0.1:8000/runs/RUN_ID/approvals/PROMPT_ID/decision \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: local-tenant" \
     -H "X-Idempotency-Key: approve-001" \
     -d '{"action": "approve", "prompt_version": 1, "decision_payload": {}}'
   ```

4. Repeat the same request and confirm the idempotent outcome is returned.
5. Submit a different action with the same key and confirm
   `idempotency_conflict`.
6. Submit a stale prompt version and confirm the latest status is returned
   without mutating the run.

## Artifact Access Validation

1. Complete a run that produces artifacts.
2. List artifacts:

   ```bash
   curl http://127.0.0.1:8000/runs/RUN_ID/artifacts \
     -H "X-Tenant-ID: local-tenant"
   ```

3. Create a download URL:

   ```bash
   curl -X POST http://127.0.0.1:8000/runs/RUN_ID/artifacts/ARTIFACT_ID/download-url \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: local-tenant" \
     -H "X-Idempotency-Key: artifact-url-001" \
     -d '{}'
   ```

4. Confirm the URL expires and cannot be reused outside the authorized platform
   context.

## API Callback Validation

1. Register a per-run callback:

   ```bash
   curl -X POST http://127.0.0.1:8000/runs/RUN_ID/callbacks \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: local-tenant" \
     -H "X-Idempotency-Key: callback-001" \
     -d '{
       "callback_url": "https://example.test/platform-callback",
       "event_types": ["terminal", "waiting_prompt", "artifact_ready"]
     }'
   ```

2. Move the run to a subscribed event state.
3. Confirm callback attempts are signed, include `event_id`, `run_id`,
   `trace_id`, and retry status, and never change the run lifecycle when
   delivery fails.

## Required Verification Before Review

Run the quality suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Review evidence must include Web UI, Telegram, and REST coverage for
invocation, live or persisted progress, status retrieval, terminal
notifications, final result retrieval, approval/resume/cancel, artifact URL
grants, duplicate idempotency handling, rate limiting, and README guidance.
