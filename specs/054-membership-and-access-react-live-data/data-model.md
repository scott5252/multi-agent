# Data Model: Membership And Access React Live Data

## Principal Identity

- **Source**: `PrincipalIdentity`
- **Fields rendered**: `principal_identity_id`, safe display label, masked email/contact label, safe subject suffix, principal status, last access summary, authorized actions.
- **Fields never rendered**: raw external subject, raw IdP claims, provider credentials, tokens, full email address, unauthorized tenant labels.
- **Relationships**: May have tenant memberships, role grants, access decision records, and membership audit records.
- **Validation rules**: Only identities visible to the active platform or tenant scope may appear. Suspended/reactivated status actions require platform authority and durable audit evidence.

## Tenant Membership

- **Source**: `TenantMembership`
- **Fields rendered**: `tenant_membership_id`, tenant id/label for authorized scope, membership status, revision token, source, status reason, authorized actions.
- **Relationships**: Belongs to one tenant and one principal identity; may originate from an invitation or administrative assignment.
- **State transitions**: `active`, `suspended`, and `removed` status changes are allowed only through membership service actions and must update revision/audit evidence.
- **Validation rules**: Cross-tenant membership IDs return denied or not found without exposing labels. Self-removal of required access is denied safely.

## User Invitation

- **Source**: `UserInvitation`
- **Fields rendered**: `invitation_id`, authorized tenant id/label, masked email, email hash label, requested role codes, status, expiration label, replay state, next-request effect, audit reference.
- **Fields never rendered**: invited raw email after creation, link tokens, delivery secrets, unauthorized tenant labels.
- **State transitions**: `pending`, `accepted`, `expired`, `revoked`, and `replayed` are distinguishable through safe status and audit evidence.
- **Validation rules**: Idempotency replay returns the persisted invitation and does not create duplicate rows.

## Role Grant

- **Source**: `RoleGrant`
- **Fields rendered**: `role_grant_id`, principal label, scope type, authorized tenant id/label, role code/label, status, effective/revoked labels, next-request effect, audit reference, authorized actions.
- **Relationships**: Belongs to one principal identity; tenant-scoped grants may create or reactivate a tenant membership.
- **State transitions**: Active grants may be revoked through membership service guardrails. Duplicate active grants replay safely.
- **Validation rules**: Tenant administrators may only assign permitted tenant roles. Platform roles require platform authority.

## Access Decision Record

- **Source**: `AccessDecisionRecord`
- **Fields rendered**: decision id, safe principal label, authorized tenant label, surface key, requested action, decision, reason, trace id/reference, timestamp, audit reference.
- **Relationships**: May point to a principal identity and tenant.
- **Validation rules**: Lists are bounded and filtered by active scope. Raw request payloads, stack traces, and unauthorized tenant labels are absent.

## Support Override

- **Source**: Existing persisted support override or audit-backed override evidence when available.
- **Fields rendered**: safe status, requester summary, approver summary, authorized target scope, expiration, decision, and audit references.
- **Validation rules**: Platform-only data remains hidden from tenant-only principals. If no persisted override model is present for the scope, the React response reports unavailable or empty rather than inventing records.

## Membership Audit Record

- **Source**: `MembershipAuditRecord` plus safe audit repository/service summaries when available.
- **Fields rendered**: audit reference id, action, decision, safe actor label, safe target label, timestamp, trace reference, summary, redacted metadata.
- **Fields never rendered**: raw metadata, raw payloads, full external identifiers, stack traces, tokens, secrets, local filesystem paths.
- **Validation rules**: Audit timeline is append-only, bounded, sorted newest first, and filtered by active scope.

## Membership Action Result

- **Source**: Service mutation result plus repository/audit evidence.
- **Fields rendered**: accepted, replayed, denied, stale, validation, unavailable, or confirmation-required status; safe summary; toast; optional invitation/principal/grant/membership summary; revision/conflict details; field errors; audit reference; next-request effect.
- **Validation rules**: Success requires persisted state or idempotent replay. Stale or denied actions never fabricate success evidence.

## Empty And Provenance State

- **Source**: Computed from live query results and backend scope resolution.
- **Fields rendered**: source kind, generated timestamp, scope id/type, empty reason, empty summary, unavailable/denied reason where safe.
- **Validation rules**: Empty arrays remain empty. The system must not synthesize placeholder users, grants, invitations, decisions, overrides, or audits.
