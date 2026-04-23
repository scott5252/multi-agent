# Foundation Runbook

## Operational Checklist

- Confirm `/health/live` returns `200`.
- Confirm `/health/ready` returns `200` only after configuration, database,
  auth, migrations, and worker dependencies are healthy.
- Confirm `/dependencies` reports the expected status for `config`, `auth`,
  `postgres`, `migrations`, and `worker`.
- Confirm `trace_id` is present on API responses and in worker startup logs.
- Confirm protected route denials create durable access-decision audit records
  without raw token or secret material.

## Auth Operations

### Auth Modes

- `AUTH_MODE=auth0` is the production path and requires `AUTH0_DOMAIN`,
  `AUTH0_ISSUER`, and `AUTH0_AUDIENCE`.
- `AUTH_MODE=local_principal` is permitted only in `local`, `test`, and `ci`,
  and requires a non-empty deterministic `LOCAL_PRINCIPAL_CATALOG_JSON`.
- Protected routes must fail closed when auth configuration is invalid.

### Support Overrides

- Platform-admin tenant access requires a persisted support-override request.
- The requester must not approve their own override.
- Approval by a second platform admin must be durable and time-bounded.

### Delegated Credentials

- `DelegatedCredentialLink` records must only reference `user_delegated`
  secret references.
- Approved tool IDs and scopes may be stored; raw tokens, refresh tokens, and
  client secrets must not be persisted or copied into audit payloads.

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
- Auth0 startup validation must fail fast when issuer, audience, or domain
  settings are missing.
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
- JWKS failure review: verify Auth0 JWT validation failures return deny
  responses without leaking raw token material.
- Delegated-credential review: verify approved-tool enforcement and secret-free
  audit evidence for delegated access.

## Workflow Registry Operations

### Local Browser QA

- Use `/auth/local-login?redirect_to=/admin/workflows/ui` for local browser
  access when `AUTH_MODE=local_principal`.
- Use `platform-admin` for publish and sharing-grant checks.
- Use `tenant-admin-acme` to verify tenant-scoped drafting and granted platform
  asset visibility.

### Draft And Publish Recovery

1. If publish returns `409`, re-fetch the draft and re-run validation.
2. If publish returns `503`, verify artifact storage and rerun publish.
3. If a platform asset is missing for a tenant, confirm the exact published
   version has an active sharing grant.
4. If a draft is unexpectedly immutable, confirm its status is
   `published_source` and create a successor draft from the published version.

### Workflow Registry Review Notes

- Validation messages should stay field-targeted and clear for blocked drafts.
- Published versions must remain immutable after artifact write and DB commit.
- Platform sharing grants must not mutate the published bundle.
- Draft authoring must remain free of secret values and delegated-credential
  payloads.
