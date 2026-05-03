 Break user administration into file-specific TDD tasks.
Include tests for user list visibility, platform invite, tenant invite,
existing Auth0 subject linking, placeholder principal creation,
idempotent invite replay, role grant creation, role grant revocation,
suspension/reactivation, tenant admin cannot assign platform roles,
cross-tenant denial, next-request role change behavior, audit records,
local-principal dev behavior, UI rendering, and API contracts. Include
implementation tasks under users/, api/routers/admin_users.py,
api/schemas/users.py, db/models/user_management.py, repositories,
extensions to admin/service.py or new user service, auth policy entries,
migration, docs, PR review notes, testing instructions, and README
updates.