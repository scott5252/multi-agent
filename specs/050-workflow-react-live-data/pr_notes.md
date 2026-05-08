# PR Notes: QA050 Workflow React Live Data

## Summary

- Replaced deterministic workflow React registry, create, builder, detail, version, lookup, publish-gate, and mutation payloads with live workflow service projections or truthful empty/unavailable states.
- Added workflow provenance, empty-state, pagination, sorting, nullable detail, and durable action request/response contracts.
- Updated React workflow pages and generated client contracts to handle empty-draft envelopes, nullable validation/publish readiness, live registry metadata, and backend-owned mutation actions.
- Updated route, schema, service, scanner, performance, and frontend tests for live workflow data and retired Spec 030 workflow markers.

## Validation

- `uv run ruff check tests/unit/api/test_admin_workflow_builder_schema.py src/multi_agent_platform/api/schemas/admin_workflow_builder.py scripts/frontend/generate_admin_react_types.py`
- `uv run pytest --no-cov tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_platform_tenant_and_auth0_are_safe tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_save_validate_and_publish_paths tests/integration/api/test_admin_workflow_ui.py tests/integration/api/test_admin_workflows_api.py tests/contract/test_admin_react_contract.py tests/unit/api/test_admin_workflow_builder_schema.py tests/unit/api/test_workflow_builder_schemas.py tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/workflows/test_workflow_builder_queries.py -q`
- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `cd frontend/admin && npm run typecheck`
- `cd frontend/admin && npm test -- --run src/components/workflows/WorkflowBuilderPage.test.tsx src/components/workflows/WorkflowGraphPanel.test.tsx src/components/workflows/WorkflowReferencePicker.test.tsx src/components/workflows/WorkflowPublishPanel.test.tsx src/components/workflows/WorkflowSectionForm.test.tsx src/components/workflows/WorkflowValidationPanel.test.tsx src/components/workflows/WorkflowRevisionPanel.test.tsx`
- `cd frontend/admin && npm run build`

## Reviewer Focus

- Confirm empty `/admin/app/workflows` state has no fixed Spec 030 workflow draft.
- Confirm seeded workflow rows, graph, validation, publish readiness, and revisions come from durable services.
- Confirm create/save/validate/restore/copy/publish actions return backend service outcomes.
- Confirm generated contracts accept nullable empty workflow detail state and no production route emits fake workflow evidence.
