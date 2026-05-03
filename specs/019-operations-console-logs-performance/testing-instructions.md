# Testing Instructions: Operations Console Logs And Performance

## Focused Test Command

```bash
uv run pytest --no-cov \
  tests/unit/operations \
  tests/unit/api/test_operations_schemas.py \
  tests/unit/api/test_operations_ui_models.py \
  tests/unit/auth/test_operations_policy.py \
  tests/contract/test_operations_console_contract.py \
  tests/integration/api/test_admin_operations_api.py \
  tests/integration/api/test_admin_operations_ui.py \
  tests/performance/operations/test_log_filtering.py \
  tests/docs/test_operations_console_docs.py
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual API Review

1. Copy `specs/019-operations-console-logs-performance/.env.qa019` to `.env`.
2. Start PostgreSQL and run migrations.
3. Start the API on `127.0.0.1:8000`.
4. Call `/admin/operations/api/dashboard` as `platform-admin`.
5. Call `/admin/operations/api/logs` as `auditor`.
6. Attempt `/admin/operations/api/dashboard` as `tenant-admin-acme` and expect
   `403`.
7. Export logs with `POST /admin/operations/api/logs/export` as
   `platform-admin`.
8. Confirm the export artifact is a redacted CSV.
9. Confirm an inspection-access audit event id is returned.
10. Confirm no raw log file is required or read.

## Manual Browser Review

1. Open `/auth/local-login?redirect_to=/admin/operations`.
2. Sign in as `platform-admin`.
3. Confirm the page renders under the admin shell.
4. Confirm dashboard cards cover health, capacity, providers, channels,
   reliability, latency, throughput, token usage, and error rate.
5. Submit filters for trace id, tenant id, run id, component, severity, status,
   dependency, and limit.
6. Confirm table rows are redacted and bounded.
7. Export the current filter set.
8. Sign in as `auditor` and confirm operations views are accessible.
9. Sign in as `tenant-admin-acme` and confirm access is denied.
10. Capture screenshots and search them for forbidden values.

## Forbidden Values

The following must not appear in rendered admin UI, JSON responses, CSV exports,
screenshots, diagnostics, or audit-safe metadata:

- real provider API keys
- authorization headers
- raw prompts
- model completions
- private channel messages
- raw request or response payloads
- memory content
- credentials
- stack traces
- unauthorized tenant data
