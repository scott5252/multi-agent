# Platform Quickstart

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2

## Local Setup

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Choose an auth mode:
   `AUTH_MODE=local_principal` for deterministic local identities in
   `local`/`test`/`ci`, or `AUTH_MODE=auth0` for production-style Auth0
   validation.
4. Start PostgreSQL with `docker compose up -d postgres`.
5. Optionally start MinIO for S3-compatible storage validation:
   `docker compose --profile storage up -d minio`.
6. Apply migrations with `uv run alembic upgrade head`.

### Local Principal Example

Use a deterministic non-production catalog entry:

```bash
export AUTH_MODE=local_principal
export LOCAL_PRINCIPAL_HEADER=X-Local-Principal
export LOCAL_PRINCIPAL_CATALOG_JSON='{"tenant-admin-acme":{"catalog_key":"tenant-admin-acme","display_name":"Tenant Admin","tenant_id":"11111111-1111-1111-1111-111111111111","org_id":"org-acme","role_codes":["tenant_user","tenant_admin"],"permission_codes":["tenant:read","tenant:admin"]}}'
```

## Run The Services

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Start the worker in another shell:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Validate The Foundation

Run the full local quality workflow:

```bash
./scripts/check.sh
```

Capture operational smoke output against a running API:

```bash
./scripts/smoke_foundation.sh
```

Run auth/access validation explicitly:

```bash
uv run pytest tests/contract/test_access_control_contract.py tests/integration/api/test_auth_routes.py tests/integration/auth/test_support_overrides.py
```

## Troubleshooting

- `503 /health/ready`: confirm `.env` is present, PostgreSQL is reachable, and
  `uv run alembic upgrade head` has run successfully, and confirm auth settings
  are valid for the selected `AUTH_MODE`.
- `401` or `403` on protected routes: verify the local principal exists in
  `LOCAL_PRINCIPAL_CATALOG_JSON`, or verify the Auth0 token issuer, audience,
  org claim, permissions, and tenant context.
- Support override access stays denied: ensure a second platform admin approved
  the request and the override is still active.
- Missing artifacts in local mode: verify `FILESYSTEM_STORAGE_ROOT` exists and
  is writable.
- Secret lookup failures in local mode: confirm the configured static secret or
  `MAP_SECRET_*` variable exists for the requested reference.
- Recovery validation: rerun `uv run alembic downgrade -1` followed by
  `uv run alembic upgrade head` before opening a PR.

## Related Docs

- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
