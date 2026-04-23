# Implementation Plan: Platform Authentication And Authorization

**Branch**: `002-platform-auth-access` | **Date**: 2026-04-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-platform-auth-access/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a production Auth0 authentication path and a non-production deterministic
local-principal path to the FastAPI platform by introducing a dedicated auth
subsystem, dependency-based authorization checks, tenant-aware principal
resolution, durable role and support-override records, access-decision audit
logging, and delegated-credential linkage that keeps raw secret material behind
the existing secret-provider boundary.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic Settings, SQLAlchemy 2.x, Alembic,
psycopg 3, httpx, pytest, pytest-asyncio, PyJWT-compatible JWT validation,
Ruff, mypy, uv  
**Storage**: PostgreSQL for tenants, role grants, support overrides, delegated
credential metadata, and access-decision audit records; existing secret
provider and object-storage abstractions remain the only path to secret or blob
material  
**Testing**: pytest, pytest-asyncio, FastAPI dependency overrides, httpx,
OpenAPI contract validation, coverage enforcement at >=90 percent for relevant
auth/authz code  
**Target Platform**: Linux container deployment target for the FastAPI API and
worker processes; local development on macOS/Linux; backend contracts consumed
by external API clients and the current or future Web UI. This feature does not
modify standalone frontend source files; it delivers the backend contracts and
principal-context metadata that a Web UI will consume for route and control
gating  
**Project Type**: Multi-tenant backend platform with API and worker entrypoints  
**Performance Goals**: Warm-path auth dependency overhead p95 <25ms; protected
request p95 <150ms for metadata-backed checks; cold JWKS refresh <500ms when
Auth0 is reachable; local-principal path p95 <10ms  
**Constraints**: Production must use Auth0; local-principal mode is allowed
only in `local`, `test`, and `ci`; all protected surfaces are explicitly
classified and default deny when unclassified; tenant access fails closed;
access decisions must be durable and secret-free; support overrides require a
second approver; raw OAuth tokens and platform secrets never enter logs or
PostgreSQL audit payloads  
**Scale/Scope**: Initial scope covers one shared FastAPI API process and one
worker process, three role families (`tenant_user`, `tenant_admin`,
`platform_admin`), low-thousands of protected requests per minute, and
tenant-aware delegated credential metadata for approved tool execution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Role grants, support overrides, delegated-credential links, and access-decision records are persisted in PostgreSQL; privileged override approval is modeled as durable state. |
| Immutable State And Memory | PASS | Access decisions and approval records are append-only or state-transitioned records; request memory is not authoritative for role changes or support approvals. |
| Contract-First Agent Coordination | PASS | Auth/session and admin access flows are described in an OpenAPI contract before implementation; policy classifications are modeled explicitly. |
| Security With Practical Development Ergonomics | PASS | Production uses Auth0 JWT validation; local/test/ci can use deterministic local principals only via explicit non-production configuration while preserving the same authorization path. |
| Operability Is A Product Requirement | PASS | The plan adds structured access-decision logs, metrics, traces, readiness failures for auth misconfiguration, and runbook updates. |
| Spec-Driven Delivery | PASS | Clarified spec, research, data model, quickstart, and contract artifacts exist before task generation. |
| Test And Documentation Discipline | PASS | The plan includes >=90 percent unit-test coverage for relevant code, contract and integration coverage, README updates, and quickstart updates. |
| Clear Ownership And Small Safe Changes | PASS | The work is split across `auth/`, `api/`, `db/`, `audit/`, `config/`, and targeted tests so later tasks can remain incremental and reviewable. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant context comes from validated token claims or deterministic local-principal fixtures and is enforced by dependency checks, repositories, and support-override boundaries. |
| Version-Pinned Execution | PASS | Runtime auth policy version, surface classification version, and claim-mapping logic remain explicit and can be included in future execution bundles without schema churn. |
| Secret Hygiene And Controlled Tool Access | PASS | Delegated OAuth credentials remain references plus metadata, never raw values; platform secrets stay behind the existing secret-provider interface; approved tool bindings are explicit and auditable. |
| Tiered Storage For Large Payloads | PASS | This feature stores only transactional metadata in PostgreSQL and does not introduce new blob payloads. |
| Human Approval Is Durable State | PASS | Tenant-specific support overrides require a persisted request, second approver decision, and auditable resume path before privileged access is granted. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/002-platform-auth-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── access-control.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── multi_agent_platform/
    ├── admin/
    │   ├── service.py
    │   └── support_overrides.py              # new
    ├── api/
    │   ├── deps.py
    │   ├── main.py
    │   ├── routers/
    │   │   ├── ops.py
    │   │   ├── auth.py                       # new
    │   │   └── admin_access.py               # new
    │   └── schemas/
    │       ├── ops.py
    │       └── auth.py                       # new
    ├── audit/
    │   ├── models.py
    │   ├── service.py
    │   └── access.py                         # new
    ├── auth/
    │   ├── principal.py
    │   ├── claims.py                         # new
    │   ├── config.py                         # new
    │   ├── dependencies.py                   # new
    │   ├── jwt_validator.py                  # new
    │   ├── local_principals.py               # new
    │   ├── policy.py                         # new
    │   └── service.py                        # new
    ├── bootstrap/
    │   └── container.py
    ├── config/
    │   └── settings.py
    ├── db/
    │   ├── models/
    │   │   ├── audit.py
    │   │   ├── access_control.py             # new
    │   │   └── delegated_credential.py       # new
    │   ├── repositories/
    │   │   ├── audit.py
    │   │   ├── access_control.py             # new
    │   │   └── delegated_credential.py       # new
    │   └── session.py
    ├── observability/
    │   ├── logging.py
    │   ├── metrics.py
    │   └── tracing.py
    ├── runtime/
    │   ├── versioning.py
    │   └── health/
    │       ├── checks.py
    │       └── service.py
    ├── secrets/
    │   └── base.py
    ├── tenancy/
    │   ├── context.py
    │   ├── guards.py
    │   └── middleware.py
    └── workers/
        └── main.py
tests/
├── contract/
│   └── test_access_control_contract.py       # new
├── integration/
│   ├── api/
│   │   ├── test_auth_modes.py                # new
│   │   ├── test_auth_routes.py               # new
│   │   ├── test_authorization_failures.py    # new
│   │   └── test_readiness_failures.py        # new
│   └── auth/
│       ├── test_delegated_credentials.py     # new
│       ├── test_platform_secret_boundaries.py # new
│       └── test_support_overrides.py         # new
├── fixtures/
│   ├── config.py
│   └── providers.py
└── unit/
    ├── api/
    │   └── test_auth_dependencies.py         # new
    ├── audit/
    │   └── test_access_audit.py              # new
    ├── auth/
    │   ├── test_jwt_validator.py             # new
    │   ├── test_local_principals.py          # new
    │   ├── test_policy.py                    # new
    │   └── test_service.py                   # new
    ├── config/
    │   └── test_auth_settings.py             # new
    ├── db/
    │   └── test_access_control_models.py     # new
    └── runtime/
        └── test_versioning.py                # new
README.md
docs/quickstart.md
docs/foundation-runbook.md
```

**Structure Decision**: Keep authentication and authorization as a first-class
platform module inside `src/multi_agent_platform/auth/`, with FastAPI route and
dependency integration in `api/`, durable metadata in `db/`, and audit-focused
recording in `audit/`. This matches the foundation’s thin-entrypoint pattern,
lets the same authorization service be reused by API and worker contexts, and
keeps user-delegated credential metadata separate from the existing
platform-secret provider boundary.

## Failure Recovery And Durability Decisions

- **Checkpoint Boundaries**: Persist role grants, protected-surface
  classifications, support-override requests and approvals, delegated-credential
  linkage metadata, and access-decision records in PostgreSQL. Protected
  requests that mutate state must write their auth decision and business change
  inside the same unit of work where feasible; support-override approval is its
  own durable transaction boundary.
- **Retry Strategy**: JWT key discovery and JWKS refresh use bounded retries and
  short-lived cached keys. Requests do not retry invalid-token, cross-tenant,
  or insufficient-permission failures. Repository writes for support-override
  creation and approval are idempotent by request identifier.
- **Compensation Strategy**: Support overrides can be revoked or allowed to
  expire. Role grants are revoked rather than deleted to preserve history.
  Delegated-credential links are expired or revoked without deleting underlying
  secret references. No compensating action is needed for denied access beyond
  recording the outcome.
- **Idempotency Strategy**: Support-override requests use a caller-provided or
  server-generated idempotency key keyed to requester, target tenant, and open
  request status. Access-decision records use a unique decision identifier and
  trace correlation rather than deduplicating across requests. Role grants are
  upserted by principal, role, scope, and effective window.

## Tenant Isolation And Fair Use Decisions

- **Tenant Context Propagation**: For Auth0 mode, tenant context is extracted
  from validated token claims, preferring `org_id` and optionally validating
  `org_name` when present. For local-principal mode, tenant context comes from a
  deterministic local-principal catalog entry. The resolved tenant context is
  stored in `ScopeContext` and propagated through request handling, audit
  records, and future worker envelopes.
- **Isolation Controls**: Tenant-scoped roles require a matching tenant
  identity. Protected routes default deny until explicitly classified. Platform
  admins stay platform-scoped unless they enter an approved support override for
  a target tenant. Repository guards continue to reject tenant mismatches.
- **Quota And Fairness Controls**: This feature does not introduce new runtime
  quotas, but access-decision metrics and support-override records include
  tenant identifiers so future quota and fairness enforcement can distinguish
  privileged support activity from ordinary tenant traffic.

## Subworkflow And Parent-Child Lineage Decisions

- **Subworkflow Boundaries**: No new reusable subworkflow runtime is introduced.
  The auth service remains a shared dependency callable from API handlers and
  future worker/task execution entrypoints.
- **Parent-Child Run Model**: Existing runtime lineage stays unchanged. The
  design adds principal, tenant, and decision correlation fields that can attach
  to future run records without changing auth storage schemas.
- **Replay And Debug Visibility**: Access-decision records, support-override
  requests, and admin role changes are queryable by `trace_id`, `request_id`,
  tenant, and principal so future lineage tools can join them to workflow runs.

## Version Bundle And Contract Decisions

- Terminology note: this plan uses `role grant` as the implementation term for
  the spec's `Role Assignment`, `protected-surface classification` as the
  canonical term for policy surface labeling, and
  `delegated-credential linkage` as the persistence model for the spec's
  `Delegated Credential Reference`.
- **Pinned Bundle Contents**: Future execution bundles should include auth
  policy version, protected-surface classification version, and claim-mapping
  version in addition to workflow, prompt, model, and tool-policy versions.
- **Resume Policy**: Resumed human approvals for support overrides reuse the
  originally persisted override request plus current approver policy checks.
  Role revocations take effect on the next protected action or token refresh,
  not by mutating past decisions.
- **Contract Compatibility Plan**: API additions for session inspection, role
  grant administration, and support overrides are documented in
  `contracts/access-control.openapi.yaml`. Future contract changes remain
  additive unless a later spec explicitly approves a breaking access-control
  migration.
- **Control Plane Boundary**: Protected-surface classifications and auth-mode
  selection are deployment-managed controls in this feature, not mutable
  runtime-admin settings.

## Secret Management And Tool Policy Decisions

- **Secret Manager Integration**: Platform-managed secrets continue to resolve
  only through `SecretProvider`. New auth configuration is settings-based and
  validated at startup; production refuses to start if Auth0 mode is selected
  without complete issuer, audience, and domain configuration.
- **Delegated Credential Handling**: User-delegated OAuth credentials are
  represented as `user_delegated` secret references plus tenant-, owner-, and
  tool-binding metadata in a dedicated linkage table. Access decisions reference
  only the linkage identifier and redacted metadata. Raw delegated tokens never
  appear in PostgreSQL, logs, traces, or audit payloads.
- **Tool Access Policy**: Approved tools are modeled explicitly on each
  delegated-credential link. Tool execution must validate the acting principal,
  tenant context, support-override state, and approved tool binding before
  resolving the underlying secret reference.
- **Platform-Managed Secret Action Control**: Platform-managed secrets may be
  resolved only through explicitly named platform actions that are classified in
  authorization policy and audited as separate from user-delegated credential
  use.

## Artifact Storage Decisions

- **Transactional Metadata**: PostgreSQL stores role grants, support overrides,
  delegated-credential linkage, access-decision records, and admin audit events.
- **Blob Storage**: Not applicable for this feature. No new object-storage
  payloads are introduced because tokens and secrets remain external.
- **Retention And Access**: Auth metadata follows audit-retention policy in
  PostgreSQL. Access to support-override and delegated-credential records is
  itself authorization-protected and queryable only through approved admin
  surfaces.

## Approval And Resume Decisions

- **Approval Triggers**: Tenant-specific support override requests from
  platform admins require explicit justification and a second authorized
  approver before the override becomes active.
- **Persisted Wait State**: Support-override requests remain in a durable
  `pending` state until approved, rejected, expired, or revoked. Approval
  decisions resume access only through the persisted approval record.
- **Audit Trail**: The platform records request creation, approval, rejection,
  expiration, and each privileged access decision that relied on an approved
  override.

## Observability Requirements

- **Logs**: Structured JSON logs with `trace_id`, `request_id`, `tenant_id`,
  `principal_id`, `auth_mode`, `surface_key`, `decision`, and redacted
  `reason_code`. Logs must never include bearer tokens, raw JWKS payloads, or
  secret values.
- **Metrics**: Counters for auth successes, unauthenticated failures,
  authorization denials by reason, cross-tenant denials, support-override
  approvals, support-override denials, JWKS refresh failures, and local-principal
  activations. Histograms track auth dependency latency and access-decision
  persistence latency.
- **Traces**: Trace spans wrap principal resolution, JWT validation, policy
  evaluation, support-override lookups, delegated-credential authorization, and
  access-decision persistence.
- **Timeline And Replay**: Operators need timeline views keyed by
  `trace_id/request_id` that show token or local-principal resolution,
  classification lookup, policy outcome, and any support-override reference.
- **Operational Runbooks**: Update README and quickstart guidance with Auth0
  configuration troubleshooting, local-principal troubleshooting, expected 401/
  403/503 failure patterns, and approval-flow validation steps.

## Test Strategy

- **Unit Tests**: Cover auth settings validation, JWT claim normalization,
  tenant extraction, role mapping, local-principal catalog resolution, protected
  surface classification, support-override policy checks, delegated-credential
  authorization rules, and access-audit recording with a target of >=90 percent
  coverage for touched auth/authz code.
- **Integration And Contract Tests**: Validate the access-control OpenAPI
  contract, `/auth/me` principal-context responses, role-grant administration,
  support-override request and approval flows, and protected endpoint behavior
  across Auth0-mode stubs and local-principal mode.
- **Failure And Recovery Tests**: Exercise missing or invalid Auth0 settings,
  JWKS refresh failures, invalid issuer/audience, missing `org_id`, revoked role
  grants, stale sessions, audit repository failures, support overrides missing a
  second approver, and delegated-credential expiry or tenant mismatch.
- **Operational Validation**: Validate readiness behavior for production auth
  misconfiguration, smoke-test local-principal mode in `local` and `test`,
  verify access-decision metrics/logs/traces, and collect PR evidence for
  allowed plus denied paths. Readiness must fail when production Auth0 mode is
  selected and issuer, audience, JWKS, or required auth metadata dependencies
  are unavailable.

## Documentation Tasks

- **README.md Updates**: Document the auth mode matrix (`auth0` vs
  `local_principal`), required Auth0 settings, deterministic local-principal
  usage, protected-surface classifications, and audit expectations.
- **Quickstart Updates**: Extend `docs/quickstart.md` and the feature quickstart
  with Auth0 setup, local-principal examples, protected-route smoke tests, and
  support-override approval validation.
- **Feature Docs**: Add API/admin contract docs for principal-context
  inspection, role-grant administration, support overrides, and delegated
  credential linkage. Update any operator runbook that references access-denied
  diagnostics.
- **PR Evidence Requirements**: Require coverage summary, contract-test output,
  protected-route allow/deny examples, local-principal smoke output, and audit
  evidence for at least one denied path and one approved support override.

## Security Review Notes

- **Auth/Authz Impact**: This feature introduces production Auth0 JWT
  validation, explicit auth modes, route-level authorization dependencies,
  support-override approvals, and user-delegated credential linkage.
- **Tenant/Security Boundaries**: Reviewers must verify `org_id` or local
  tenant context validation, fail-closed behavior for unclassified routes,
  deny-overrides-allow policy resolution, and the inability to activate local
  principals in production.
- **Secret/Tool Risk Review**: Reviewers must verify that delegated credentials
  remain references only, approved tool bindings are enforced, support overrides
  cannot grant raw secret access, and audit payloads are redacted.
- **Additional Review Needed**: Security review should explicitly inspect JWKS
  caching behavior, admin approval separation-of-duty enforcement, and 401/403/
  503 response mappings for sensitive failure modes.
