# Testing Instructions: Model Provider Gateway

Use this document for reviewer evidence. For a full copy/paste walkthrough,
start with `qa011.md`; for web-only reviewer steps, use `QA011_UI.MD`.

## Automated Checks

```bash
uv sync
uv run alembic upgrade head
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Admin Web UI QA

1. Open `/admin/model-providers` as a platform administrator.
2. Create an OpenAI connection with at least one model, capability metadata,
   cost metadata, timeout policy, tenant visibility, and secret references.
3. Create a local OpenAI-compatible connection with an allowlisted base URL.
4. Verify create/edit/detail/test results/catalog pages all render inside the
   shared admin shell.
5. Run safe tests for both providers and verify health, latency, outcome,
   normalized reason, tested model, and safe diagnostics are visible.
6. Confirm the catalog page shows healthy selectable entries and collision
   warnings when a tenant-scope model id collision is attempted.
7. Sign in as a tenant-scoped user and verify only visible rows appear and
   mutation/test controls are unavailable.

Expected evidence:

- `/admin/model-providers` shows display name, provider type, active state,
  health, last-test outcome, model count, tenant visibility, catalog sync
  status, and updated timestamp.
- `/admin/model-providers/new` and edit pages include provider type, display
  name, base URL, model ids, timeout policy, tenant visibility, active state,
  and secret-reference id fields.
- Detail pages show safe metadata, latest health, latest test, model
  definitions, tenant visibility, and test/sync actions.
- `/admin/model-providers/catalog` shows tenant scope, provider type, model id,
  health state, availability, selectability, and governing connection.

## API QA

1. Exercise connection create/update/activate/deactivate/test/sync endpoints
   with platform-admin credentials.
2. Repeat mutation and test requests with tenant-scoped credentials and verify
   safe denial plus audit evidence.
3. Verify local base URLs outside the allowlist are rejected before network
   calls.
4. Verify missing, revoked, inactive, or tenant-inappropriate secret references
   fail closed.

## Provider Mock QA

Use mocked `httpx` transports for:

- OpenAI success with usage metadata.
- OpenAI authorization failure.
- Local provider success without usage metadata.
- Timeout, rate limit, provider unavailable, invalid model, and malformed
  response failures.

## Runtime QA

1. Run a workflow that requires a model call and verify invocation uses
   `ModelGateway`.
2. Run a test bench model call and verify it uses the same gateway path.
3. Inspect invocation metadata for selected catalog entry, connection, model,
   latency, outcome, retry inputs, breaker inputs, and usage availability.
4. Force transient provider failures and verify retry/breaker behavior.
5. Force non-retryable failures and verify no retry is attempted.

## Secret Hygiene QA

Search provider connection rows, catalog entries, test results, invocation
attempts, logs, traces, audit summaries, and docs fixtures for:

- Raw API keys
- Provider tokens
- Authorization headers
- URL userinfo
- Prompt text
- Completion text
- Raw provider response bodies
- Local endpoint secrets

Expected result: zero matches except safe placeholder names in tests/docs.

## Performance QA

Run the gateway latency performance test with mocked providers and verify p95
gateway overhead is <= 25 ms excluding provider network delay.
