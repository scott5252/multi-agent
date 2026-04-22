# Foundation Runbook

## Operational Checklist

- Confirm `/health/live` returns `200`.
- Confirm `/health/ready` returns `200` only after configuration, database,
  migrations, and worker dependencies are healthy.
- Confirm `/dependencies` reports the expected status for `config`, `postgres`,
  `migrations`, and `worker`.
- Confirm `trace_id` is present on API responses and in worker startup logs.

## Controlled Recovery

### Local Or CI Recovery

1. Run `uv run alembic downgrade -1`.
2. Run `uv run alembic upgrade head`.
3. Run `./scripts/check.sh`.
4. Run `./scripts/smoke_foundation.sh` against a local API session.

### Production-Oriented Expectations

- Migration rollback is validated in local and CI before promotion.
- Readiness must fail closed on stale migrations or unavailable worker
  dependencies.
- Tenant-scoped data must not be enqueued, stored, or queried across tenant
  boundaries.
- Secrets must only be referenced through provider adapters; raw secret values
  must not be persisted in audit or application tables.

## Review Notes

- Tenant isolation review: verify queue, artifact, and audit access stays bound
  to the active `ScopeContext`.
- Secret redaction review: verify logs and audit payloads mask keys such as
  `token`, `password`, `authorization`, and `api_key`.
- Migration recovery review: verify the downgrade and re-upgrade workflow still
  produces the expected table set and readiness outcome.
