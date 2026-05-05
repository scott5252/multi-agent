# Spec 029 Reviewer Notes

## Scope

Spec 029 adds a React operations, reliability, and run debug workbench on top of
the existing React admin shell.

The visible route is `/admin/app/operations`.

The API contract route is `/admin/app/operations.json`.

The run debug route is `/admin/app/operations/runs/{workflow_run_id}.json`.

The safe export route is `/admin/app/operations/export`.

The page is deterministic for QA. It does not call live providers, Telegram, or
external connector tools.

## Implementation Summary

- Added backend workbench schemas for health cards, likely causes, health
  panels, run timelines, graph branches, gateway attempts, tool calls, channel
  deliveries, reliability recovery, logs, and export snapshots.
- Added deterministic operations aggregation builders with platform and tenant
  scope variants.
- Added protected FastAPI routes for the operations shell, workbench envelope,
  run debug envelope, and export snapshot.
- Extended generated React API contracts and drift checks for Spec 029 models.
- Added React client helpers and workbench components for summaries, timeline,
  reliability, export, and page composition.
- Routed `/admin/app/operations` through the React shell and removed it from
  the disabled-route fallback list.
- Added backend, contract, frontend, route, redaction, tenant-isolation,
  cross-tenant denial, export, and bounded-query tests.

## Security Notes

- Backend routes remain protected by local-principal/Auth0-shaped principal
  authorization.
- Tenant scope resolution uses the existing admin shell helpers and fails
  closed before data renders.
- Platform-only provider and pressure summaries are hidden from tenant scope.
- Unsafe filters return safe validation problem details without echoing raw
  input.
- Export snapshots expose `artifact-ref-qa029-*` references, not local paths.
- Workbench schema validators reject QA029 secret markers, raw provider
  responses, private channel messages, provider authorization strings, and raw
  tool results.
- QA fixtures use fake `qa029/` secret references only.

## Validation Log

Focused backend validation:

- `uv run ruff check src/multi_agent_platform/api/schemas/admin_workbench.py src/multi_agent_platform/operations/workbench.py src/multi_agent_platform/api/routers/admin_react.py tests/unit/api/test_admin_workbench_schema.py tests/unit/operations/test_workbench_service.py tests/performance/operations/test_workbench_queries.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py scripts/frontend/generate_admin_react_types.py` passed.
- `uv run mypy src/multi_agent_platform/api/schemas/admin_workbench.py src/multi_agent_platform/operations/workbench.py src/multi_agent_platform/api/routers/admin_react.py` passed.
- `uv run pytest tests/unit/api/test_admin_workbench_schema.py tests/unit/operations/test_workbench_service.py tests/unit/api/test_admin_patterns_schema.py tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py tests/performance/operations/test_workbench_queries.py --no-cov` passed.

Focused frontend validation:

- `cd frontend/admin && npm run typecheck` passed.
- `cd frontend/admin && npm run test -- --run` passed.
- `cd frontend/admin && npm run build` passed.
- `uv run python scripts/frontend/generate_admin_react_types.py --check` passed.

Repository quality validation:

- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml` passed, including `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.

QA validation:

- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/029-operations-reliability-and-run-debug-workbench` passed.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml --dry-run` passed.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml --dry-run --start-processes` passed.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml` passed.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml --start-processes` passed after aligning the manifest expectation with the visible `Recovery posture` heading.
- Screenshot inspection passed for denied, platform, export, and tenant workbench flows.

## Evidence Paths

- `specs/029-operations-reliability-and-run-debug-workbench/qa029.md`
- `specs/029-operations-reliability-and-run-debug-workbench/qa029_ui.md`
- `specs/029-operations-reliability-and-run-debug-workbench/qa029_user_guide.md`
- `specs/029-operations-reliability-and-run-debug-workbench/.env.qa029`
- `output/playwright/qa029_ui/qa029-react-operations-denied.png`
- `output/playwright/qa029_ui/qa029-react-operations-platform.png`
- `output/playwright/qa029_ui/qa029-react-operations-export.png`
- `output/playwright/qa029_ui/qa029-react-operations-tenant.png`

## Reviewer Checklist

- Confirm `/admin/app/operations` denies unauthenticated access.
- Confirm `platform-admin` can load the platform workbench.
- Confirm `auditor` can load the platform workbench.
- Confirm `tenant-admin-acme` can load the tenant workbench.
- Confirm platform view shows health, queue pressure, provider health, likely
  cause, run debug, reliability, logs, and export evidence.
- Confirm tenant view shows tenant run health and tenant delivery.
- Confirm tenant view hides platform-only provider health.
- Confirm run debug shows branch, gateway, tool, delivery, lineage, and replay
  summaries without raw data.
- Confirm export returns `artifact-ref-qa029-platform` or
  `artifact-ref-qa029-tenant`.
- Confirm Acme cannot access Globex scope.
- Confirm no `qa029-secret-value`, `/Users/`, raw prompt, raw completion,
  memory content, provider authorization header, private channel message, raw
  provider response, raw connector output, stack trace, or Globex tenant data
  appears for Acme.
