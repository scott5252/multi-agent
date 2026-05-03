dd user and tenant membership administration. Platform
admins must be able to list users, create invitations, link or provision
Auth0-backed principal identities, assign platform roles, assign tenant
roles, suspend or reactivate users, revoke grants, and inspect user
access history across tenants. Tenant admins must be able to invite users
to their own tenant, assign permitted tenant roles, revoke tenant
memberships, and view user status for their tenant only. The platform
must store principal metadata, invitations, memberships, and role grants,
but production authentication remains Auth0-backed and the platform must
not store user passwords. Local-principal mode must remain available for
development and test. All role changes must take effect on the next
protected action and create audit records. Require idempotent invites,
safe email handling, tenant isolation, at least 90 percent coverage,
docs, PR notes, testing instructions, and README updates.
