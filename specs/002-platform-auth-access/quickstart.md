# Quickstart: Platform Authentication And Authorization

## Purpose

Validate production-style Auth0 JWT protection, deterministic local-principal
mode for development and tests, role-based protected routes, support-override
approval flow, and delegated-credential authorization boundaries.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2
- An Auth0 tenant with:
  - a custom API configured for this platform
  - RBAC enabled for the API
  - permissions defined for protected surfaces
  - organization support if tenant context is derived from `org_id`

## 1. Install dependencies

```bash
uv sync
```

## 2. Prepare environment configuration

```bash
cp .env.example .env
```

Core auth settings to define:

- `AUTH_MODE=auth0` for production-style validation
- `AUTH_MODE=local_principal` for deterministic non-production principals
- `AUTH0_DOMAIN`
- `AUTH0_ISSUER`
- `AUTH0_AUDIENCE`
- `AUTH0_REQUIRED_ORG_CLAIM=true`
- `LOCAL_PRINCIPAL_CATALOG_JSON=...` for local/test/ci only
- `LOCAL_PRINCIPAL_HEADER=X-Local-Principal` when exercising deterministic
  local identities

Expected startup rules:

- `AUTH_MODE=auth0` is valid in every environment, including production
- `AUTH_MODE=local_principal` is allowed only in `local`, `test`, or `ci`
- startup must fail fast when production selects `local_principal` or when
  Auth0 mode is missing required issuer, audience, or domain settings

## 3. Start infrastructure and apply migrations

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

## 4. Run the API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 5. Validate local-principal mode

Set non-production auth mode:

```bash
export AUTH_MODE=local_principal
```

Use a deterministic local principal from the configured catalog:

```bash
curl \
  -H "X-Local-Principal: tenant-admin-acme" \
  http://127.0.0.1:8000/auth/me
```

Expected result:

- the response shows resolved principal identity, tenant context, role set, and
  auth mode `local_principal`
- protected tenant-admin endpoints succeed only for matching tenant principals
- cross-tenant or underprivileged calls return `403`
- support-override and role-grant endpoints use the same identity resolution
  path as protected tenant routes

## 6. Validate Auth0 mode

Set production-style auth mode:

```bash
export AUTH_MODE=auth0
```

Call a protected route with a valid Auth0 access token:

```bash
curl \
  -H "Authorization: Bearer $AUTH0_ACCESS_TOKEN" \
  http://127.0.0.1:8000/auth/me
```

Smoke-test a denied call:

```bash
curl \
  -H "Authorization: Bearer $AUTH0_ACCESS_TOKEN" \
  http://127.0.0.1:8000/admin/support-overrides
```

Expected result:

- invalid issuer, audience, signature, or organization claims return `401`
  or `403` depending on the failure class
- valid tokens lacking required role or permission return `403`
- Auth0/JWKS connectivity or auth metadata failures on protected surfaces return
  `503` and should also surface through readiness checks

## 7. Validate support-override approval flow

1. Authenticate as a `platform_admin`.
2. Create a tenant-specific support override request with justification.
3. Approve it using a different authorized approver.
4. Retry the tenant-specific support action.

Expected result:

- request creation is persisted as `pending`
- approval by the requester is rejected
- access remains denied until a second approver records approval
- approved tenant-specific access is auditable and linked to the override

## 8. Validate delegated-credential boundaries

1. Create or load a `user_delegated` secret reference for a tenant user.
2. Link it to one approved tool identifier and a limited scope set.
3. Attempt one authorized tool call and one unauthorized tool call.

Expected result:

- only the approved tool action resolves the secret reference
- cross-tenant or unapproved-tool usage is denied
- audit records reference the delegated-credential link identifier, not secret
  material

## 9. Run automated validation

Targeted auth tests:

```bash
uv run pytest tests/unit/auth tests/unit/api tests/unit/audit tests/integration/api tests/integration/auth tests/contract
```

Full coverage validation:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Static validation:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Contract-focused validation:

```bash
uv run pytest tests/contract/test_access_control_contract.py tests/integration/api/test_auth_routes.py tests/integration/auth/test_support_overrides.py
```

## 10. Troubleshooting

- `401 Unauthorized`: verify issuer, audience, signature, expiration, and
  presence of required claims such as `org_id`
- `403 Forbidden`: verify protected-surface classification, role grants, token
  permissions, tenant context, and support-override approval state
- `503 Service Unavailable` on protected routes: verify JWKS reachability,
  database-backed auth metadata availability, and audit persistence health
- local-principal request rejected in local/test: verify the principal exists in
  the configured deterministic catalog and the header uses the exact catalog key
- startup failure in production: verify `AUTH_MODE=auth0` and that all Auth0
  settings are present
