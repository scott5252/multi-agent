# PR Notes: QA034 React Membership Administration

## Summary

- Added safe backend React contracts for membership administration.
- Added deterministic membership adapter projections for platform and tenant views.
- Added /admin/app/memberships React route, mutations, access history, and audit endpoints.
- Added generated TypeScript contracts, client helpers, React components, fixtures, and tests.
- Preserved the existing /admin/memberships Jinja fallback.

## Validation

- uv run python scripts/frontend/generate_admin_react_types.py --check
- uv run pytest --no-cov tests/unit/api/test_admin_membership_react_schema.py tests/unit/admin/memberships/test_react_membership_service.py tests/performance/memberships/test_react_membership_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
- cd frontend/admin && npm run typecheck && npm run test && npm run build
- bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/034-react-user-and-tenant-membership-administration
- uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml
- uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml --start-processes

## Review Focus

- Tenant admins must not see Globex while scoped to Acme.
- Platform admins may see authorized Globex labels.
- Invite replay must be explicit and idempotent.
- Platform-only role grants must fail closed for tenant admins.
- Raw identity values must remain outside the primary UI.
