# Admin Memberships UI Contract

## Route

- `GET /admin/memberships`

## Audience

- Platform admins can view platform scope and any selected tenant.
- Tenant admins are scoped to their own tenant.
- Unauthenticated or underprivileged users are redirected or denied by the
  existing admin shell authorization flow.

## Page Requirements

The page title is `Membership Administration`.

The first viewport must show:

- Selected scope summary.
- Invitation form with email, requested tenant roles, and optional tenant id for
  platform admins.
- Principal search/list with masked email, provider, status, role summary, and
  membership summary.
- Access history and membership audit summaries with safe trace ids.

## Forms

Invitation form:

- `POST /admin/memberships/invitations`
- Fields: `tenant_id`, `email`, `requested_roles`, `idempotency_key`.
- Expected success: Redirect back to `/admin/memberships` with the same tenant
  scope and an audit row.
- Expected denial: 403 without cross-tenant details.

Role grant form:

- `POST /admin/memberships/role-grants`
- Fields: `principal_identity_id`, `scope_type`, `tenant_id`, `role_code`.
- Tenant admins may submit only tenant-scoped `tenant_user` or `tenant_admin`
  roles for their tenant.

Status forms:

- `POST /admin/memberships/principals/{principal_identity_id}/suspend`
- `POST /admin/memberships/principals/{principal_identity_id}/reactivate`
- `POST /admin/memberships/memberships/{tenant_membership_id}/suspend`
- `POST /admin/memberships/memberships/{tenant_membership_id}/restore`
- `POST /admin/memberships/memberships/{tenant_membership_id}/remove`

## Redaction

The UI must render masked email displays and safe subject labels. It must never
render passwords, raw tokens, or raw external secrets. Flash messages must refer
to "invitation", "membership", or masked email text only.

## Screenshot Evidence

The Playwright validation captures:

- `01-local-login.png`
- `02-user-tenant-membership-administration-target.png`
- `03-user-tenant-membership-administration-direct-target.png`
