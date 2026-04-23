# Research: Platform Authentication And Authorization

## Decision 1: Use FastAPI `Security()` dependencies as the single authorization entrypoint

- **Decision**: Implement authentication and authorization through centralized
  FastAPI dependencies that use `Security()` and `SecurityScopes`, then fan out
  to shared auth services for token validation, local-principal resolution, and
  policy checks.
- **Rationale**: FastAPI’s security dependency model lets the platform declare
  required scopes per route while keeping the actual policy evaluation in one
  place. This fits the existing `api/deps.py` pattern, keeps OpenAPI output
  aligned with route protection, and allows the same dependency tree to switch
  between Auth0 JWT validation and deterministic local principals.
- **Alternatives considered**:
  - Use only middleware for authorization: rejected because route-specific scope
    and role requirements would become implicit and harder to test.
  - Use the Auth0 FastAPI SDK directly at every route: rejected because the repo
    needs an internal wrapper that can support local principals, database-backed
    role grants, and custom support-override policies without scattering vendor
    coupling throughout route handlers.
- **Sources**:
  - [FastAPI `Security()` reference](https://fastapi.tiangolo.com/reference/dependencies/)
  - [FastAPI OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
  - [Auth0 FastAPI quickstart](https://auth0.com/docs/quickstart/backend/fastapi/index)

## Decision 2: Validate Auth0 access tokens with issuer, audience, permission, and organization checks

- **Decision**: In Auth0 mode, validate JWT signature and standard claims
  against Auth0 issuer and audience configuration, then enforce permission and
  organization checks before deriving platform principal context.
- **Rationale**: Auth0’s guidance requires standard JWT validation plus audience
  and permission verification, and its organization guidance explicitly requires
  checking `org_id` against a trusted application mapping. That aligns directly
  with the platform’s tenant-isolation requirements.
- **Alternatives considered**:
  - Validate only the JWT signature: rejected because issuer, audience,
    permissions, and organization checks are required to prevent token replay
    across APIs or tenants.
  - Treat Auth0 tokens as opaque and call back to Auth0 for each request:
    rejected because Auth0 custom API access tokens are self-contained JWTs and
    the platform wants stateless request validation on the hot path.
- **Sources**:
  - [Validate Access Tokens](https://auth0.com/docs/secure/tokens/access-tokens/validate-access-tokens)
  - [Work with Tokens and Organizations](https://auth0.com/docs/manage-users/organizations/using-tokens)
  - [Access Tokens](https://auth0.com/docs/secure/tokens/access-tokens)

## Decision 3: Normalize token claims, but keep platform authorization authoritative in PostgreSQL

- **Decision**: Treat Auth0 as the source of authenticated identity and tenant
  organization context, but keep platform role grants, protected-surface
  classifications, and support-override approvals in PostgreSQL as the
  authoritative authorization layer.
- **Rationale**: The platform spec requires role changes to take effect on the
  next protected action, local-principal parity in non-production, and durable
  auditability for support overrides. A database-backed authorization model
  satisfies those requirements better than relying on Auth0 role claims alone,
  while still allowing Auth0 permissions to be used as an outer gate for API
  access.
- **Alternatives considered**:
  - Use only Auth0 roles and permissions for all app authorization: rejected
    because local principals, tenant-specific support overrides, and next-action
    revocations would become harder to model and audit.
  - Use only application database roles and ignore token permissions: rejected
    because it discards Auth0 API RBAC signals that can prevent obviously
    unauthorized tokens from reaching deeper platform policy checks.
- **Sources**:
  - [Role-Based Access Control](https://auth0.com/docs/manage-users/access-control/rbac)
  - [Authorization Policies](https://auth0.com/docs/manage-users/access-control/authorization-policies)
  - [Platform auth spec](./spec.md)

## Decision 4: Support both Auth0 access-token profiles by normalizing claims internally

- **Decision**: Normalize claim extraction so the platform accepts Auth0 access
  tokens that follow either the default Auth0 profile or the RFC 9068 profile,
  provided the token includes the required audience and authorization claims.
- **Rationale**: Auth0 documents two access-token profiles with small claim
  differences such as `azp` versus `client_id` and optional `jti`. Normalizing
  these differences inside the auth service avoids coupling the platform to one
  tenant configuration while still allowing richer audit data when `jti` is
  present.
- **Alternatives considered**:
  - Force only one Auth0 token profile now: rejected because the repository does
    not yet control every possible Auth0 tenant configuration for future
    environments.
  - Ignore token profile differences: rejected because audit and client
    attribution need stable internal fields.
- **Sources**:
  - [Access Token Profiles](https://auth0.com/docs/secure/tokens/access-tokens/access-token-profiles)

## Decision 5: Model deterministic local principals as a non-production auth mode, not a mock bypass

- **Decision**: Replace the foundation’s simple boolean `auth_enabled` toggle
  with an explicit auth mode configuration that supports `auth0` and
  `local_principal`, where local principals are resolved from a deterministic
  catalog and flow through the same authorization service as Auth0 principals.
- **Rationale**: The constitution requires practical development ergonomics
  without erasing production’s security model. A dedicated `local_principal`
  mode makes the bypass explicit, blocks accidental production use, and ensures
  the authorization code path stays identical after principal resolution.
- **Alternatives considered**:
  - Keep a boolean `auth_enabled` flag and inject a hard-coded system principal:
    rejected because it does not exercise role resolution, tenant scoping, or
    deny-path audit behavior.
  - Allow callers to send arbitrary local roles in headers: rejected because it
    would turn dev/test into an unbounded privilege-injection path instead of a
    deterministic catalog of known principals.
- **Sources**:
  - [Platform constitution](../../.specify/memory/constitution.md)
  - [Platform auth spec](./spec.md)

## Decision 6: Persist access decisions and privileged approvals durably before treating access as granted

- **Decision**: Store access decisions, support-override requests, support
  approvals, and role-grant changes in PostgreSQL, and fail closed for protected
  requests when the platform cannot resolve required auth metadata or persist
  privileged approval state.
- **Rationale**: The spec requires auditability of access decisions and durable
  approval state for tenant-specific support overrides. Persisting this metadata
  transactionally keeps security review and incident response grounded in
  authoritative records instead of best-effort logs.
- **Alternatives considered**:
  - Emit access decisions only to logs: rejected because logs alone do not
    satisfy the durable audit requirement or approval wait-state requirement.
  - Write audit records asynchronously after the response: rejected because a
    crash between authorization and write completion would create a non-audited
    privileged action.
- **Sources**:
  - [Platform constitution](../../.specify/memory/constitution.md)
  - [Platform auth spec](./spec.md)

## Decision 7: Link user-delegated OAuth credentials to approved tools through metadata, not raw token storage

- **Decision**: Represent user-delegated OAuth credentials as `SecretReference`
  records with `user_delegated` scope plus a separate linkage record that binds
  the credential to the owning principal, tenant, approved tool identifiers,
  allowed scopes, and lifecycle state.
- **Rationale**: The foundation already separates secret references from raw
  secret values, and the auth spec explicitly requires user-delegated
  credentials to stay distinct from platform-managed secrets. A linkage record
  lets the platform enforce who may trigger which tool with a delegated
  credential while keeping raw OAuth material outside application persistence
  and audit payloads.
- **Alternatives considered**:
  - Store delegated OAuth refresh/access tokens directly in an auth table:
    rejected because it violates the secret-hygiene boundary and expands the
    breach surface.
  - Reuse platform-managed secret semantics without an ownership link: rejected
    because delegated credentials must remain tied to a specific user and tenant
    and cannot act as platform identity.
- **Sources**:
  - [Token Best Practices](https://auth0.com/docs/secure/tokens/token-best-practices)
  - [Platform foundation data model](../001-platform-foundation/data-model.md)
  - [Platform auth spec](./spec.md)
