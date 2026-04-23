# Data Model: Platform Authentication And Authorization

## Overview

The authentication and authorization feature adds durable identity, policy, and
audit metadata on top of the platform foundation so the API can validate Auth0
JWTs in production, resolve deterministic local principals in non-production,
enforce tenant-aware role grants, and link user-delegated credentials to
approved tool execution without storing raw secret material.

Existing `Tenant`, `SecretReference`, and `AuditEvent` entities from the
platform foundation remain in use and are extended by the entities below.

## Core Entities

### PrincipalIdentity

| Field | Type | Notes |
|---|---|---|
| `principal_identity_id` | UUID | Primary key |
| `auth_provider` | enum | `auth0`, `local_principal`, `system` |
| `external_subject` | text | Stable provider subject (`sub` or local catalog key) |
| `display_name` | text nullable | Human-readable label |
| `email` | text nullable | Optional contact identity |
| `status` | enum | `active`, `suspended` |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last metadata update |

**Validation rules**

- `auth_provider + external_subject` is unique.
- Local principals use deterministic, human-readable catalog keys and are never
  created dynamically from arbitrary request input.

**Relationships**

- One principal has many role grants, support-override requests, support
  approvals, access-decision records, and delegated-credential links.

### RoleGrant

| Field | Type | Notes |
|---|---|---|
| `role_grant_id` | UUID | Primary key |
| `principal_identity_id` | UUID | FK to `PrincipalIdentity` |
| `scope_type` | enum | `platform`, `tenant` |
| `tenant_id` | UUID nullable | Required for tenant-scoped roles |
| `role_code` | enum | `tenant_user`, `tenant_admin`, `platform_admin` |
| `grant_source` | enum | `bootstrap`, `admin_assignment`, `local_catalog`, `sync` |
| `status` | enum | `active`, `revoked`, `expired` |
| `effective_at` | timestamptz | Grant effective time |
| `expires_at` | timestamptz nullable | Optional expiry |
| `granted_by_principal_id` | UUID nullable | Approver or system actor |
| `revoked_at` | timestamptz nullable | Revocation timestamp |
| `updated_at` | timestamptz | Last mutation timestamp |

**Validation rules**

- Tenant-scoped roles require `tenant_id`.
- `platform_admin` grants must use `scope_type = platform`.
- Only one active grant per principal, role, scope, and tenant combination.

**State transitions**

- `active -> revoked`
- `active -> expired`

### ProtectedSurfacePolicy

| Field | Type | Notes |
|---|---|---|
| `protected_surface_policy_id` | UUID | Primary key |
| `surface_type` | enum | `api_route`, `web_route`, `tool_action` |
| `surface_key` | text | Stable identifier such as `GET:/auth/me` |
| `classification` | enum | `public`, `tenant_user`, `tenant_admin`, `platform_admin` |
| `required_permissions` | JSONB | Required Auth0 permissions, if any |
| `required_roles` | JSONB | Required platform roles |
| `deny_rules` | JSONB | Explicit deny conditions and override requirements |
| `policy_version` | text | Version label for policy evolution |
| `enabled` | boolean | Classification toggle |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last mutation timestamp |

**Validation rules**

- `surface_key` is unique.
- All non-public surfaces must declare at least one role, permission, or deny
  rule.
- Newly added surfaces are not routable until a policy row or code-backed
  classification exists.

### SupportOverrideRequest

| Field | Type | Notes |
|---|---|---|
| `support_override_request_id` | UUID | Primary key |
| `requester_principal_id` | UUID | Platform admin requesting tenant access |
| `target_tenant_id` | UUID | Tenant to be entered |
| `justification` | text | Human-entered reason |
| `status` | enum | `pending`, `approved`, `rejected`, `expired`, `revoked` |
| `approver_principal_id` | UUID nullable | Second authorized approver |
| `requested_at` | timestamptz | Request timestamp |
| `decided_at` | timestamptz nullable | Approval or rejection time |
| `expires_at` | timestamptz nullable | Active-override expiry |
| `request_trace_id` | text | Correlation ID |
| `idempotency_key` | text | Duplicate protection key |

**Validation rules**

- Requester and approver must be different principals.
- Only platform-admin requesters may open support overrides.
- Only approved requests may be referenced by tenant-specific support access.

**State transitions**

- `pending -> approved`
- `pending -> rejected`
- `pending -> expired`
- `approved -> revoked`
- `approved -> expired`

### AccessDecisionRecord

| Field | Type | Notes |
|---|---|---|
| `access_decision_record_id` | UUID | Primary key |
| `principal_identity_id` | UUID nullable | Nullable for anonymous denials |
| `scope_type` | enum | `platform`, `tenant` |
| `tenant_id` | UUID nullable | Required for tenant-scoped evaluations |
| `surface_key` | text | Evaluated route, page, or tool action |
| `requested_action` | text | Semantic action name |
| `decision` | enum | `allow`, `deny`, `error` |
| `reason_code` | enum | `unauthenticated`, `invalid_token`, `insufficient_permission`, `insufficient_role`, `cross_tenant`, `support_override_required`, `support_override_unapproved`, `config_error`, `delegated_credential_denied`, `internal_error` |
| `auth_mode` | enum | `auth0`, `local_principal` |
| `token_subject` | text nullable | Auth token subject when present |
| `token_jti` | text nullable | Token identifier when present |
| `support_override_request_id` | UUID nullable | FK to `SupportOverrideRequest` |
| `delegated_credential_link_id` | UUID nullable | FK to `DelegatedCredentialLink` |
| `trace_id` | text | Correlation ID |
| `request_id` | text nullable | HTTP request correlation |
| `occurred_at` | timestamptz | Decision timestamp |

**Validation rules**

- Anonymous denials may omit `principal_identity_id`, but all decisions must
  include `surface_key`, `reason_code`, and `trace_id`.
- `decision = allow` requires a resolved principal unless the surface is
  explicitly public.

### DelegatedCredentialLink

| Field | Type | Notes |
|---|---|---|
| `delegated_credential_link_id` | UUID | Primary key |
| `secret_reference_id` | UUID | FK to existing `SecretReference` |
| `owner_principal_id` | UUID | FK to `PrincipalIdentity` |
| `tenant_id` | UUID | Owning tenant |
| `approved_tool_ids` | JSONB | Allowlisted tool identifiers |
| `granted_scopes` | JSONB | Redacted OAuth scopes only |
| `status` | enum | `active`, `revoked`, `expired` |
| `provider_subject` | text nullable | External account reference, not secret material |
| `granted_at` | timestamptz | Grant timestamp |
| `expires_at` | timestamptz nullable | Optional expiry |
| `revoked_at` | timestamptz nullable | Revocation timestamp |
| `last_used_at` | timestamptz nullable | Last authorized use |

**Validation rules**

- Backing `SecretReference` must use `scope_type = user_delegated`.
- `approved_tool_ids` may not be empty when status is `active`.
- No raw access token, refresh token, or client secret value is stored in this
  record.

**State transitions**

- `active -> revoked`
- `active -> expired`

## Supporting Non-Persistent Models

### PrincipalContext

A request-scoped model produced by Auth0 JWT validation or local-principal
resolution:

- `principal_identity_id`
- `principal_id`
- `auth_provider`
- `auth_mode`
- `tenant_id`
- `org_id`
- `role_codes`
- `permission_codes`
- `support_override_request_id`
- `trace_id`
- `request_id`

### AuthorizationDecision

A service-level evaluation result returned by the central auth dependency:

- `surface_key`
- `requested_action`
- `classification`
- `decision`
- `reason_code`
- `required_roles`
- `required_permissions`
- `evaluated_at`

### LocalPrincipalCatalogEntry

Configuration model for deterministic non-production principals:

- `catalog_key`
- `display_name`
- `tenant_id`
- `role_codes`
- `permission_codes`
- `enabled`

## Relationship Summary

- `PrincipalIdentity 1 -> N RoleGrant`
- `PrincipalIdentity 1 -> N SupportOverrideRequest` as requester
- `PrincipalIdentity 1 -> N SupportOverrideRequest` as approver
- `PrincipalIdentity 1 -> N AccessDecisionRecord`
- `PrincipalIdentity 1 -> N DelegatedCredentialLink`
- `Tenant 1 -> N RoleGrant`
- `Tenant 1 -> N SupportOverrideRequest`
- `Tenant 1 -> N AccessDecisionRecord`
- `Tenant 1 -> N DelegatedCredentialLink`
- `SecretReference 1 -> 0..N DelegatedCredentialLink`
- `SupportOverrideRequest 1 -> 0..N AccessDecisionRecord`

## Notes For Planning

- Access-decision records are intentionally specialized rather than hidden in a
  generic JSON audit payload so operators can query denials, override use, and
  delegated-credential authorizations without brittle payload parsing.
- Role grants and delegated-credential links rely on immutable identity keys
  from `PrincipalIdentity`, which lets Auth0 users and deterministic local
  principals share the same authorization service.
- Support-override approval is the only in-scope human wait-state for this
  feature and therefore gets its own lifecycle model instead of being inferred
  indirectly from generic audit entries.
