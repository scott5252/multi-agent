# Quickstart: Workflow React Live Data

## Goal

Validate that Spec 050 replaces workflow React deterministic builder data with live, authorized workflow projections and durable mutations.

## Prerequisites

- Docker PostgreSQL is available.
- `uv sync` has completed.
- Node dependencies under `frontend/admin` are installed.
- Specs 048 and 049 changes are present in the dirty worktree.

## QA Environment

Spec validation uses:

- Feature directory: `specs/050-workflow-react-live-data`
- Validation manifest: `specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml`
- QA env file: `specs/050-workflow-react-live-data/.env.qa050`
- QA database: `multi_agent_platform_qa050`
- Playwright output: `output/playwright/qa050_ui`
- Curl regression output: `.data/curl_test_runs/qa050-after-spec`

## Focused Backend Checks

Run focused tests while implementing:

```bash
uv run pytest --no-cov tests/unit/api/test_admin_workflow_builder_schema.py tests/contract/test_workflow_builder_contract.py -q
uv run pytest --no-cov tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py -q
uv run pytest --no-cov tests/integration/api/test_admin_workflow_ui.py tests/integration/api/test_admin_workflows_api.py -q
uv run pytest --no-cov tests/unit/admin/test_live_data_inventory_scanner.py -q
```

## Frontend Checks

```bash
cd frontend/admin
npm run typecheck
npm test -- --run src/components/workflows src/App.test.tsx
npm run build
```

## Generated Contract Check

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Empty-State Verification

After the QA database is migrated with no workflow seed records:

1. Request `/admin/app/workflows/registry.json` as an authorized local principal.
2. Verify `items` is empty.
3. Verify provenance/empty-state metadata explains that no workflows exist.
4. Verify create actions are present only when the principal is authorized.
5. Verify no fixed `qa030`, `DEFAULT_DRAFT_ID`, fake graph node, fake publish evidence, or fake audit reference appears.

## Seeded-State Verification

Seed at least one Acme tenant workflow draft through durable repositories, services, migrations intended for QA, or admin APIs:

- Workflow lineage.
- Active draft.
- At least two draft revisions.
- Latest validation result.
- Required publish-gate/test-bench evidence.
- Published bundle.
- Sharing state where authorized.
- Optional cross-scope isolation records.

Then verify:

1. `/admin/app/workflows/registry.json` lists the durable seeded workflow.
2. `/admin/app/workflows/drafts/{workflow_draft_id}/detail.json` returns the same durable draft ID and latest revision token.
3. Graph preview nodes and edges match the stored workflow document.
4. `/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate.json` reflects live missing/stale/failing/passing evidence.
5. `/admin/app/workflows/versions/{workflow_version_bundle_id}/detail.json` reflects the durable published bundle.
6. Cross-tenant requests fail closed without unauthorized names or tenant labels.

## Mutation Verification

Use backend route tests and Playwright to exercise at least one user-visible durable workflow action:

- Create a draft, or
- Save/edit a draft revision, and
- Run validation, and
- Attempt publish or inspect publish-gate readiness.

Post-UI verification must prove persistence through an API assertion first and a direct QA database query when the API cannot expose the needed evidence safely.

## Full Spec Validation

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/050-workflow-react-live-data
```

Run Spec QA:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml
```

Run Playwright:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml --start-processes
```

Run post-UI API/database verification and record exact command output in the spec status file.

Run curl regression:

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa050-after-spec
```

## Completion Criteria

Spec 050 can be marked complete only when:

- All tasks in `tasks.md` are checked.
- QA050 docs and env file exist.
- Focused backend checks pass.
- Frontend typecheck, tests, and build pass.
- Generated TypeScript contract check passes.
- Spec QA passes.
- Playwright passes and captures QA050 workflow screenshots.
- Post-UI API/database verification proves durable workflow state.
- Multi-agent curl regression passes.
- `status.json.history` includes completed entries for implement, validation, and spec completion before queue advancement.
