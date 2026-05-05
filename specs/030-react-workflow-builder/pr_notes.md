# PR Notes: Spec 030 - React Workflow Builder

## Summary

Implemented the React workflow builder at `/admin/app/workflows`.

Added backend-owned builder, lookup, save, validation, and publish contracts.

Added generated TypeScript contracts and React client helpers for workflow builder data.

Added guided authoring, reference picker, React Flow graph preview, validation, publish evidence, revision history, and redacted JSON preview components.

Preserved existing Jinja workflow routes.

## Safety Notes

No live provider, Telegram, credential, or connector calls are used by QA030.

All builder data is deterministic and redaction-safe.

The UI renders artifact references instead of local paths.

Cross-tenant requests fail closed before rendering builder data.

Raw prompts, completions, memory contents, private channel messages, provider responses, Telegram updates, and tool payloads are blocked by schema validation and are not rendered in React fixtures.

## Focused Validation

- `uv run ruff check src/multi_agent_platform/api/schemas/admin_workflow_builder.py src/multi_agent_platform/admin/workflow_builder.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/auth/policy.py` - passed.
- `uv run mypy src/multi_agent_platform/api/schemas/admin_workflow_builder.py src/multi_agent_platform/admin/workflow_builder.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/auth/policy.py` - passed.
- `cd frontend/admin && npm run typecheck` - passed.
- `cd frontend/admin && npm run test` - passed, 37 tests.
- `uv run pytest --no-cov tests/unit/api/test_admin_workflow_builder_schema.py tests/unit/admin/test_workflow_builder_service.py tests/performance/workflows/test_workflow_builder_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` - passed, 29 tests.

## Pending Full Validation

Final outcomes:

- QA documents: `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/030-react-workflow-builder` - passed.
- Spec QA: `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml` - passed.
- Playwright UI validation: `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml --start-processes` - passed.
- Screenshot evidence:
  - `output/playwright/qa030_ui/qa030-react-workflows-denied.png`
  - `output/playwright/qa030_ui/qa030-react-workflows-tenant.png`
  - `output/playwright/qa030_ui/qa030-react-workflows-save.png`
  - `output/playwright/qa030_ui/qa030-react-workflows-publish.png`
  - `output/playwright/qa030_ui/qa030-react-workflows-cross-tenant.png`
