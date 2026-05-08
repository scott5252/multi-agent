# QA050 User Guide: Spec 050 - Workflow React Live Data

## Detailed Overview

QA050 makes the workflow React workspace live-data backed.

The workflow workspace lives at `/admin/app/workflows`.

Before QA050, this surface still relied on deterministic Spec 030-style workflow defaults.

Those defaults included fixed draft identifiers, fixed lineage identifiers, fixed revision names, fake graph nodes, fake publish evidence, and fake audit references.

Those values were useful for early UI migration work.

They are no longer acceptable as production-like data.

QA050 changes the workflow registry, create page, builder, draft detail, version detail, lookup catalog, publish gate, and workflow mutation actions so they read durable services or return truthful empty, denied, or unavailable states.

An empty database should show no workflow records.

It should explain that there are no durable workflows for the active scope.

It should still show authorized create actions when the principal can create workflows.

A seeded database should show only live workflow records visible to the active principal.

The builder should show the stored workflow document, graph, references, validation result, revision history, publish readiness, sharing summary, published version detail, and redacted JSON preview.

The save, validate, restore, copy, create, and publish actions should call backend services.

They should return persisted success, stale conflict, validation failure, publish denial, idempotent replay, or confirmation-needed results.

They should not return fake success.

No reviewer evidence should contain raw credentials, raw prompts, memory contents, private messages, provider payloads, tool payloads, or local absolute paths.

## Who Should Use This Guide

Use this guide if you are reviewing qa050 manually.

Use this guide if you need a plain-language checklist for workflow browser behavior.

Use this guide if you need to confirm that workflow React routes are live-data backed.

Use `qa050.md` when you need deeper API, test, and command evidence.

Use `qa050_ui.md` when you need a browser-first walkthrough with screenshot names.

Use this user guide as the short reviewer operating procedure.

## Manual QA Prerequisites

You need a local checkout of the repository.

You need Docker available for PostgreSQL.

You need Node dependencies available for the React admin build.

You need Python dependencies available through `uv`.

You need the qa050 environment file.

The environment file is `specs/050-workflow-react-live-data/.env.qa050`.

The QA database is `multi_agent_platform_qa050`.

The QA storage root is `.data/qa050-artifacts`.

The local browser base URL is `http://127.0.0.1:8000`.

The local login URL is `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.

The primary principal is `tenant-admin-acme`.

The cross-tenant principal for negative checks is `tenant-admin-globex`.

Before starting, close any server already listening on port 8000.

Before starting, save or move any unrelated `.env` file if you need it later.

## Step-by-Step Manual QA

1. Copy the environment file.

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/050-workflow-react-live-data/.env.qa050 .env
```

Expected result: `.env` contains qa050 settings.

2. Install dependencies.

```bash
uv sync
```

Expected result: dependencies install without requiring live external services.

3. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: the PostgreSQL container is running.

4. Reset the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa050 && createdb -U postgres multi_agent_platform_qa050'
```

Expected result: the qa050 database is recreated.

5. Run migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations complete cleanly.

6. Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa050 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Expected result: the seed command succeeds even if tenants already exist.

7. Build the React admin.

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected result: the React asset manifest is updated.

8. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the API is available at `http://127.0.0.1:8000`.

9. Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Expected result: the local login page lists `tenant-admin-acme`.

10. Select `tenant-admin-acme`.

Expected result: the workflow React workspace opens.

11. Review the empty workflow state.

Expected result: there are no workflow rows if the database has not been seeded, and the page shows truthful empty-state and provenance metadata.

12. Check the empty registry API.

```bash
curl -sS -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/app/workflows/registry.json' | jq '{items, empty_state, provenance, pagination}'
```

Expected result: `items` is empty and no fixed qa030 workflow identifiers are present.

13. Seed or create a workflow using the automated QA seed or backend route tests.

Expected result: a durable Acme workflow draft exists.

14. Reload the workflow page.

Expected result: the registry and builder display the durable seeded workflow.

15. Save or validate the workflow from the browser.

Expected result: the page shows a backend mutation result with safe audit/reference evidence.

16. Check the registry API again.

```bash
curl -sS -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/app/workflows/registry.json' | jq '{total: (.pagination.total_items // (.items | length)), first: .items[0]}'
```

Expected result: the API response matches the workflow visible in the browser.

17. Run the focused automated checks.

```bash
uv run pytest --no-cov tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_platform_tenant_and_auth0_are_safe tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_save_validate_and_publish_paths tests/integration/api/test_admin_workflow_ui.py tests/integration/api/test_admin_workflows_api.py tests/contract/test_admin_react_contract.py tests/unit/api/test_admin_workflow_builder_schema.py tests/unit/api/test_workflow_builder_schemas.py tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/workflows/test_workflow_builder_queries.py -q
```

Expected result: focused backend coverage passes.

18. Run frontend checks.

```bash
cd frontend/admin
npm run typecheck
npm test -- --run src/components/workflows/WorkflowBuilderPage.test.tsx src/components/workflows/WorkflowGraphPanel.test.tsx src/components/workflows/WorkflowReferencePicker.test.tsx src/components/workflows/WorkflowPublishPanel.test.tsx src/components/workflows/WorkflowSectionForm.test.tsx src/components/workflows/WorkflowValidationPanel.test.tsx src/components/workflows/WorkflowRevisionPanel.test.tsx
cd ../..
```

Expected result: workflow frontend coverage passes.

## Expected Results

The workflow page is acceptable when the empty state is truthful, seeded state is live, mutations persist through backend services, cross-tenant access is denied, and no production workflow route returns fixed Spec 030 workflow data.

The workflow page is not acceptable if it displays `qa030`, `DEFAULT_DRAFT_ID`, `DEFAULT_LINEAGE_ID`, fake publish evidence, fake graph nodes, or fake audit references as production state.

The workflow registry should show zero items in an empty qa050 database.

The workflow builder should show no active workflow draft until one is created.

The create action should create a durable workflow draft through the backend.

The save action should create a new durable revision and show a safe audit reference.

The validation and publish panels should show live readiness or honest unavailable states.

The generated React bundle should not contain old Spec 030 workflow fixture state as production behavior.

## Evidence To Capture

Capture `/tmp/qa050-ui-workflows-empty.png` for the empty workflow page.

Capture `/tmp/qa050-ui-workflows-seeded.png` after a workflow draft exists.

Capture `/tmp/qa050-ui-workflow-save.png` after saving a draft from the browser.

Capture `/tmp/qa050-ui-publish-gate.png` after viewing validation or publish readiness.

Capture `/tmp/qa050-registry-empty.json` from the empty registry API check.

Capture `/tmp/qa050-post-ui-registry.json` after the browser create or save action.

Capture the Spec QA output and the Playwright screenshot directory `output/playwright/qa050_ui`.

Capture the curl regression output under `.data/curl_test_runs/qa050-after-spec`.

## Security And Redaction Checks

Do not capture raw provider authorization headers.

Do not capture raw credentials or secret values.

Do not capture raw prompts, raw completions, memory contents, private channel messages, or external tool payloads.

Workflow graph and JSON inspector evidence should be summarized or redacted.

Mutation evidence should use safe audit/reference identifiers only.

If a response contains raw unsafe payload text, stop validation and fix the serializer before continuing.

## Tenant Isolation Checks

Use `tenant-admin-acme` for the positive workflow checks.

Use `tenant-admin-globex` for the negative cross-tenant check.

The Globex principal must not see Acme workflow names, draft IDs, graph contents, validation summaries, or tenant labels.

Platform-only workflow checks must use `platform-admin`.

Tenant-scoped workflow creation must resolve to the signed-in tenant when no explicit tenant id is supplied.

Cross-tenant identifiers should return denied or unavailable responses without leaking record details.

## Troubleshooting

If the local login page does not show `tenant-admin-acme`, confirm `.env.qa050` was copied before starting the API.

If the workflow page shows stale JavaScript behavior, rerun `npm run --prefix frontend/admin build`.

If the empty workflow state still shows rows, reset `multi_agent_platform_qa050` and rerun migrations.

If saving fails with a stale revision, reload the draft and retry with the latest revision.

If Playwright cannot click `Create draft`, inspect the browser screenshot under `output/playwright/qa050_ui`.

If curl regression fails, keep Spec 050 active and inspect `.data/curl_test_runs/qa050-after-spec` before moving to Spec 051.
