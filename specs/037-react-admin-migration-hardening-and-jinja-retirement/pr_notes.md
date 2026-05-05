# PR Notes: QA037 React Admin Migration Hardening

## Summary

- Adds the React migration hardening dashboard as the `/admin/app` landing experience and direct `/admin/app/migration` route.
- Adds backend-safe migration schemas, deterministic route projections, rollback evidence, performance budget evidence, accessibility evidence, redaction sweeps, and tenant isolation sweeps.
- Adds generated TypeScript contracts, React components, API client helpers, fixtures, and tests for migration hardening.

## Validation

- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `uv run pytest --no-cov tests/unit/api/test_admin_migration_hardening_react_schema.py tests/unit/admin/test_migration_hardening_service.py tests/performance/migration_hardening/test_react_migration_hardening_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py`
- `cd frontend/admin && npm run typecheck`
- `cd frontend/admin && npm run test`
- `cd frontend/admin && npm run build`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/037-react-admin-migration-hardening-and-jinja-retirement`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml --start-processes`

## Reviewer Focus

- Confirm no legacy route is actually deleted in QA037.
- Confirm retained fallbacks are clearly labeled.
- Confirm routes marked retirement-ready carry parity evidence.
- Confirm rollback steps and verification steps are visible.
- Confirm platform, tenant admin, and tenant user scopes differ as expected.
- Confirm cross-tenant denial does not reveal unauthorized tenant names.
- Confirm the redaction scan reports no unsafe evidence.

## Known Limits

- Legacy Jinja deletion is disabled by default.
- Retained fallback routes remain available for the soak window.
- Performance values are deterministic local QA evidence, not production SLO measurements.
- Accessibility evidence is a QA037 browser-oriented checklist and screenshot review, not a replacement for deeper manual accessibility audits.
