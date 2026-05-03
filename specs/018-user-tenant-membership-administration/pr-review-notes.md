# PR Review Notes: User And Tenant Membership Administration

## Summary

This change adds governed Membership Administration under the shared admin
shell at `/admin/memberships`. It introduces a focused membership domain
package, additive database tables for invitations, tenant memberships, and
membership audit records, JSON admin APIs, server-rendered UI, policy entries,
local-principal grant/status refresh, tests, QA docs, and quickstart updates.

## Reviewer Focus

- Verify platform admins can manage users, invitations, Auth0 subject links,
  platform role grants, tenant role grants, principal suspension, grant
  revocation, and access history.
- Verify tenant admins can manage only their own tenant and only permitted
  tenant roles.
- Verify role changes take effect on the next protected request.
- Verify raw passwords are never accepted or stored.
- Verify raw invite emails and Auth0 subject values are not rendered in API
  summaries, UI tables, audit summaries, or screenshots.
- Verify additive migration behavior for `user_invitations`,
  `tenant_memberships`, and `membership_audit_records`.

## Main Implementation Areas

- `src/multi_agent_platform/admin/memberships/`
- `src/multi_agent_platform/api/routers/admin_memberships.py`
- `src/multi_agent_platform/api/schemas/memberships.py`
- `src/multi_agent_platform/api/ui/memberships.py`
- `src/multi_agent_platform/db/models/user_management.py`
- `src/multi_agent_platform/db/repositories/memberships.py`
- `src/multi_agent_platform/auth/policy.py`
- `src/multi_agent_platform/auth/service.py`
- `src/multi_agent_platform/web_admin/templates/memberships/index.html`
- `alembic/versions/0018_user_tenant_membership_administration.py`

## Manual Evidence

- Follow `specs/018-user-tenant-membership-administration/qa018.md`.
- Follow `specs/018-user-tenant-membership-administration/qa018_ui.md`.
- Use `specs/018-user-tenant-membership-administration/.env.qa018`.
- Preserve `/tmp/qa018-*` output and `output/playwright/qa018_ui` screenshots.

## Known Boundaries

- The first implementation records invitations and local evidence; it does not
  send real email.
- Auth0 remains the external identity provider. This feature stores only
  subject references and identity metadata.
- Tenant admins are limited to tenant-scoped `tenant_user` and `tenant_admin`
  grants for their own tenant.
- Local-principal mode uses catalog permissions for bootstrapping and merges
  persisted role grants plus principal status on each protected request.

## Suggested Review Order

1. Read `spec.md`, `plan.md`, and `data-model.md`.
2. Review the Alembic migration and SQLAlchemy models.
3. Review repository and service guardrails.
4. Review policy entries and auth refresh behavior.
5. Review router schemas and UI template.
6. Run focused tests from `testing-instructions.md`.
7. Run QA018 API and browser validation.
