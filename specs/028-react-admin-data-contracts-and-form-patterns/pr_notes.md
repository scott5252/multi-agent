# Spec 028 Reviewer Notes

## Scope

Spec 028 adds reusable React admin data contracts and form patterns on top of
the existing `/admin/app` shell.

The visible sample route is `/admin/app/patterns`.

The API contract route is `/admin/app/patterns.json`.

The sample mutation route is `/admin/app/patterns/actions/sample`.

The sample export route is `/admin/app/patterns/export`.

The page is intentionally harmless. It does not mutate real workflow,
provider, credential, Telegram, memory, or tool-execution records.

## Implementation Summary

- Added backend `AdminPageEnvelope`, safe problem, filter, pagination, sorting,
  action, mutation, stale conflict, idempotency, confirmation, export, evidence,
  and sample data schemas.
- Added protected FastAPI routes for the sample patterns page, page envelope,
  sample action preview, and sample export preview.
- Extended generated React API contracts and drift checks for Spec 028 models.
- Added frontend client helpers, `AdminDataTable`, `AdminForm`,
  `useAdminMutation`, and `PatternsPage`.
- Routed `/admin/app/patterns` through the React shell while keeping existing
  Jinja admin pages available.
- Added backend, contract, frontend component, hook, and route tests for safe
  envelopes, validation, stale conflict, idempotency replay, confirmation,
  export references, redaction, denied access, and cross-tenant denial.

## Security Notes

- Backend routes remain protected by local-principal/Auth0-shaped principal
  authorization.
- Tenant scope is resolved by existing admin shell helpers and fails closed.
- Unknown filters and sort fields return safe validation problem details.
- Export snapshots expose `artifact-ref-qa028-*` references, not local paths.
- Sample mutation results use safe summaries and audit reference IDs.
- QA fixtures use fake `qa028/` secret references only.

## Validation Log

Focused backend validation:

- `uv run ruff check src/multi_agent_platform/api/schemas/admin_patterns.py src/multi_agent_platform/api/routers/admin_react.py tests/unit/api/test_admin_patterns_schema.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py scripts/frontend/generate_admin_react_types.py` passed.
- `uv run mypy src/multi_agent_platform/api/schemas/admin_patterns.py src/multi_agent_platform/api/routers/admin_react.py` passed.
- `uv run pytest tests/unit/api/test_admin_patterns_schema.py tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py --no-cov` passed.

Focused frontend validation:

- `cd frontend/admin && npm run typecheck` passed.
- `cd frontend/admin && npm run test -- --run` passed.
- `cd frontend/admin && npm run build` passed.
- `uv run python scripts/frontend/generate_admin_react_types.py --check` passed.

Repository quality validation:

- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed.
- `uv run mypy src` passed in full Spec QA.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` passed in full Spec QA.

QA validation:

- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/028-react-admin-data-contracts-and-form-patterns` passed.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml --dry-run` passed.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml --dry-run --start-processes` passed.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml` passed after correcting the protected shell HTML expectation to assert `/admin/app/bootstrap.json`; the envelope route is covered by the separate `/admin/app/patterns.json` curl check.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml --start-processes` passed.
- Screenshot inspection passed for denied, authenticated page, validation, stale conflict, and export flows.

## Evidence Paths

- `specs/028-react-admin-data-contracts-and-form-patterns/qa028.md`
- `specs/028-react-admin-data-contracts-and-form-patterns/qa028_ui.md`
- `specs/028-react-admin-data-contracts-and-form-patterns/qa028_user_guide.md`
- `specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028`
- `output/playwright/qa028_ui/qa028-react-patterns-denied.png`
- `output/playwright/qa028_ui/qa028-react-patterns-page.png`
- `output/playwright/qa028_ui/qa028-react-patterns-validation.png`
- `output/playwright/qa028_ui/qa028-react-patterns-stale.png`
- `output/playwright/qa028_ui/qa028-react-patterns-export.png`

## Reviewer Checklist

- Confirm `/admin/app/patterns` denies unauthenticated access.
- Confirm `tenant-admin-acme` can load the patterns page.
- Confirm `Forms and data patterns` and `Workflow readiness review` render.
- Confirm blank sample name returns `validation error`.
- Confirm outcome `stale` returns `stale conflict`.
- Confirm outcome `replay` returns `replayed`.
- Confirm outcome `confirmation` returns `confirmation required`.
- Confirm export preview returns `artifact-ref-qa028-tenant`.
- Confirm no `qa028-secret-value`, `/Users/`, raw prompt, raw completion,
  memory content, provider authorization header, external tool payload, or
  Globex tenant data appears for Acme.
