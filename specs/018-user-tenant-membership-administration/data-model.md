# Data Model: User And Tenant Membership Administration

## PrincipalIdentity

Existing table: `principal_identities`

- `principal_identity_id`: UUID primary key.
- `auth_provider`: `auth0`, `local_principal`, or `system`.
- `external_subject`: Auth0 subject or local-principal catalog key.
- `display_name`: Safe display name.
- `email`: Operational email value where known.
- `status`: `active` or `suspended`.

Validation:

- No password fields are accepted or persisted.
- External subject remains unique.
- Suspended identities are denied protected actions before role checks.

## UserInvitation

New table: `user_invitations`

- `user_invitation_id`: UUID primary key.
- `tenant_id`: Optional tenant scope. `null` means platform-scoped invitation.
- `invited_email`: Normalized operational email.
- `invited_email_hash`: Stable SHA-256 hash of normalized email.
- `masked_email`: Screenshot-safe email display.
- `requested_roles`: Requested role codes.
- `status`: `pending`, `accepted`, `revoked`, or `expired`.
- `idempotency_key`: Optional caller-provided key.
- `invited_by_principal_id`: Admin principal id.
- `principal_identity_id`: Linked principal after provisioning or acceptance.
- `expires_at`, `accepted_at`, `revoked_at`, `created_at`, `updated_at`.
- `trace_id`: Request trace for audit correlation.

Validation:

- Email is trimmed and lowercased before hash/idempotency checks.
- Active invite replay returns the existing pending row for the same tenant,
  email hash, requested roles, and idempotency key when provided.
- Tenant admins may create only tenant-scoped invitations for their tenant.

## TenantMembership

New table: `tenant_memberships`

- `tenant_membership_id`: UUID primary key.
- `tenant_id`: Tenant scope.
- `principal_identity_id`: Principal identity.
- `invitation_id`: Optional invitation source.
- `status`: `active`, `suspended`, or `removed`.
- `revision_token`: Current optimistic concurrency token.
- `membership_source`: `invitation`, `admin_assignment`, `auth0_link`, or
  `local_catalog`.
- `created_by_principal_id`, `updated_by_principal_id`.
- `created_at`, `updated_at`, `suspended_at`, `removed_at`.

Validation:

- One active membership projection per tenant/principal pair.
- Tenant admins may update only their own tenant memberships.
- Removed memberships are not returned as active tenant access.

## RoleGrant

Existing table: `role_grants`

- Platform grants use `scope_type=platform`, `tenant_id=null`.
- Tenant grants use `scope_type=tenant`, a tenant id, and `tenant_user` or
  `tenant_admin`.
- Revocation updates `status` and `revoked_at`; rows are not deleted.

Validation:

- Tenant admins cannot create platform grants.
- Tenant admins cannot create grants for other tenants.
- Next protected request reads active persisted grants.

## MembershipAuditRecord

New table: `membership_audit_records`

- `membership_audit_record_id`: UUID primary key.
- `tenant_id`: Optional tenant scope.
- `actor_principal_id`: Admin principal id.
- `target_principal_identity_id`: Optional target principal.
- `action`: Stable action key.
- `decision`: `allow` or `deny`.
- `summary`: Human-readable safe summary.
- `trace_id`: Request trace.
- `redacted_metadata`: JSON object with masked email, role codes, tenant id,
  grant id, reason code, and other safe values.
- `created_at`: Audit timestamp.

Validation:

- Metadata must not include raw passwords, tokens, or unmasked email display in
  screenshot-safe contexts.
- Denied service-level guardrail checks record safe audit records.

## State Transitions

Invitation:

```text
pending -> accepted
pending -> revoked
pending -> expired
```

Tenant membership:

```text
active -> suspended -> active
active -> removed
suspended -> removed
removed -> active
```

Principal identity:

```text
active -> suspended -> active
```
