# React Membership Administration UI Contract

## Route

- React route: `/admin/app/memberships`
- Existing fallback route: `/admin/memberships`
- Primary bootstrap contract: `/admin/app/memberships/bootstrap.json`

## Sections

- Overview
- Directory
- Invitations
- Role grants
- Status
- Access history
- Audit

## Required States

- Loading
- Empty directory
- Filtered empty
- Denied
- Validation error
- Stale conflict
- Idempotency replay
- Confirmation required
- Partial history unavailable
- Audit unavailable
- Unexpected error

## Platform Administrator Experience

- Shows platform and tenant scope options.
- Shows users across tenants.
- Shows invite dialog with tenant picker.
- Shows principal link/provision dialog.
- Shows platform role and tenant role grant wizard.
- Shows suspend and reactivate actions with confirmation.
- Shows grant revoke actions with confirmation.
- Shows safe access history across authorized tenants.

## Tenant Administrator Experience

- Shows only the active tenant scope.
- Shows only tenant-scoped users, invitations, memberships, grants, and history.
- Shows only permitted tenant role choices.
- Denies platform role assignment.
- Denies cross-tenant search, details, invite, grant, revoke, and status
  changes without confirming resource existence.

## Redaction Rules

- Primary user rows show display name, masked email, and safe subject suffix.
- Full raw identifiers appear only in backend-authorized detail panels.
- QA screenshots must not contain passwords, raw authorization headers,
  credential values, private messages, local paths, full external subjects, or
  unauthorized tenant labels.

## Interaction Rules

- Invite submission shows created or replayed state.
- Role grant wizard separates platform and tenant scope.
- Suspend, reactivate, remove membership, revoke grant, and principal link
  overwrite require confirmation.
- Mutation results show status, audit reference, next-request effect, and safe
  recovery actions.
- React never computes role eligibility or authorization decisions locally.
