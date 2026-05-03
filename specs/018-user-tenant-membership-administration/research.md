# Research: User And Tenant Membership Administration

## Decision: Reuse Existing Access-Control Tables For Principal And Grants

**Rationale**: `principal_identities`, `role_grants`, and
`access_decision_records` already model Auth0/local subjects, current grants,
revocation, and protected-action history. Reusing them keeps role changes
visible to the existing authorization path and avoids a second source of truth.

**Alternatives considered**: Creating parallel user and grant tables was
rejected because it would require synchronization and could let the admin UI
drift from runtime authorization.

## Decision: Add Dedicated Invitation, Tenant Membership, And Audit Tables

**Rationale**: Invitations and tenant membership lifecycle need state that is
not present in role grants: normalized email, masked display, expiry,
idempotency, invitation status, membership revision, membership status, and
safe audit payloads.

**Alternatives considered**: Encoding invitations in role grants was rejected
because invitations may exist before a principal identity or active grant.

## Decision: Normalize Emails For Idempotency And Mask In Safe Surfaces

**Rationale**: Idempotent invites require a stable comparison key, while safe
screenshots and audits should avoid full email display. The service lowercases
and trims email, stores a hash and masked display, and limits where the raw
normalized email appears.

**Alternatives considered**: Hash-only storage was rejected for the first slice
because operational invitation records need a deliverable address once email
delivery is wired.

## Decision: Tenant Admins May Only Assign Tenant Roles In Their Own Tenant

**Rationale**: The least-privilege boundary is simple and testable: tenant
admins can invite and grant `tenant_user` or `tenant_admin` in their own tenant;
platform roles and other tenants require platform admin authority.

**Alternatives considered**: A configurable role catalog was deferred because
the existing role enum is small and fixed.

## Decision: Refresh Persisted Grants On Each Protected Request

**Rationale**: Auth0 requests already read active role grants by principal. The
local-principal path should also merge persisted role grants and principal
status after catalog bootstrap so role changes and suspension are visible on
the next protected action in development and test.

**Alternatives considered**: Restarting local-principal sessions was rejected
because it would not satisfy next-request semantics and would hide regressions
from QA.

## Decision: Store Membership Audit Records In The Feature Tables

**Rationale**: Membership changes need a durable, feature-specific audit trail
that can be listed in the admin UI without joining broad platform audit tables.
Records store action, decision, tenant, principal, target, trace, and redacted
metadata.

**Alternatives considered**: Only using access-decision records was rejected
because many admin mutations are business events, not just access decisions.
