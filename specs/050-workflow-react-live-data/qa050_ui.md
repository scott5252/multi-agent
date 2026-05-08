# QA050 UI: Workflow React Live Data

## Goal

Guide a reviewer through browser evidence for qa050.

The UI review confirms that the workflow React workspace opens from local login, shows truthful empty states when no durable workflow exists, renders seeded live workflow data when present, and routes workflow actions through backend services.

## How To Use This Guide

Run the setup commands from the repository root.

Use a browser pointed at `http://127.0.0.1:8000/auth/local-login`.

Save screenshots and notes under these names:

- `/tmp/qa050-ui-login.png`
- `/tmp/qa050-ui-workflows-empty.png`
- `/tmp/qa050-ui-workflows-seeded.png`
- `/tmp/qa050-ui-workflow-save.png`
- `/tmp/qa050-ui-publish-gate.png`
- `/tmp/qa050-ui-post-api-notes.txt`

Expected: every screenshot or note file references qa050 and avoids raw secrets, private messages, raw prompt text, memory contents, provider payloads, and local absolute paths.

What is happening: the reviewer is collecting visual evidence that matches the backend API checks.

Why this matters: qa050 removes deterministic workflow data, so browser evidence must prove the UI is using live API state.

## Environment Setup

### 1. Copy the QA environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/050-workflow-react-live-data/.env.qa050 .env
uv sync
```

Expected: `.env.qa050` is active and dependencies are available.

What is happening: the app is configured for local-principal qa050 review.

Why this matters: the browser must use deterministic local principals and the `multi_agent_platform_qa050` database.

### 2. Prepare the QA database

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa050 && createdb -U postgres multi_agent_platform_qa050'
uv run alembic upgrade head
```

Expected: migrations complete without errors.

What is happening: workflow registry and builder routes will read from an empty durable database first.

Why this matters: empty workflow states must be truthful, not fabricated.

### 3. Seed tenants

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa050 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Expected: Acme and Globex tenants exist.

What is happening: local login will be able to select tenant-shaped principals.

Why this matters: workflow data must stay tenant-scoped.

### 4. Build the React assets

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected: the build writes `src/multi_agent_platform/web_admin/static/react/manifest.json`.

What is happening: FastAPI will serve the updated workflow React bundle.

Why this matters: the browser must not run stale Spec 030 deterministic assets.

### 5. Start the app

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the app starts at `http://127.0.0.1:8000`.

What is happening: the browser will use the same app instance as the API evidence.

Why this matters: qa050 acceptance needs matching browser and backend behavior.

## Browser Walkthrough

### 1. Local login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Select `tenant-admin-acme`.

Expected: the browser lands on `/admin/app/workflows` and shows the workflow React workspace.

What is happening: local-principal auth sets the safe tenant reviewer identity.

Why this matters: workflow records are tenant-scoped.

Reviewer evidence: save `/tmp/qa050-ui-login.png`.

### 2. Empty workflow state

Open:

```text
http://127.0.0.1:8000/admin/app/workflows
```

Review the registry, create panel, and builder state.

Expected: with no workflow seed, the page shows no durable workflow rows, includes a create action if authorized, and shows empty-state/provenance metadata.

What is happening: the React page is rendering `/admin/app/workflows/builder.json`, `/registry.json`, and `/lookups.json`.

Why this matters: an empty database must not render `qa030`, `DEFAULT_DRAFT_ID`, or fake graph/publish evidence.

Reviewer evidence: save `/tmp/qa050-ui-workflows-empty.png`.

### 3. Seeded workflow state

Use the automated Spec QA seed or backend route tests to create a durable Acme workflow draft.

Then reload:

```text
http://127.0.0.1:8000/admin/app/workflows
```

Expected: the registry lists the durable workflow, and the builder shows the stored draft name, revision, graph, validation summary, publish readiness, references, revision history, and safe JSON inspector.

What is happening: the UI is reading live workflow records and service projections.

Why this matters: seeded browser state must match durable API data.

Reviewer evidence: save `/tmp/qa050-ui-workflows-seeded.png`.

### 4. Save draft action

Edit the workflow name or description and select `Save draft`.

Expected: the UI shows a success or accepted result with a backend audit/reference summary, and the revision updates.

What is happening: the React client posts to `/admin/app/workflows/drafts/{workflow_draft_id}/save`.

Why this matters: save cannot be a fake mutation result.

Reviewer evidence: save `/tmp/qa050-ui-workflow-save.png`.

### 5. Validation and publish gate

Select `Run validation`, then inspect the publish panel.

Expected: validation and publish readiness reflect current backend state, required evidence, and any blockers or warnings.

What is happening: the UI reads durable validation and publish-gate projections.

Why this matters: the workflow builder cannot display fake passing evidence.

Reviewer evidence: save `/tmp/qa050-ui-publish-gate.png`.

### 6. Post-UI API verification

Run:

```bash
curl -sS -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/workflows/registry.json' \
  | tee /tmp/qa050-ui-post-registry.json \
  | jq '{total: (.pagination.total_items // (.items | length)), first: .items[0]}'
```

Expected: the registry response reflects the workflow seen or updated in the browser.

What is happening: API output is compared with browser state.

Why this matters: Playwright and manual browser evidence must be backed by durable API state.

Reviewer evidence: write the response summary to `/tmp/qa050-ui-post-api-notes.txt`.

### 7. Cross-tenant negative check

Log out or clear the local-principal session, then log in as `tenant-admin-globex`.

Open the Acme workflow draft detail URL captured from the seeded state.

Expected: the request is denied or unavailable without exposing Acme names, graph contents, validation text, or tenant labels.

What is happening: tenant authorization is enforced before workflow projection.

Why this matters: live workflow data must not leak across tenants.

## Required Automated Evidence

Run these commands after the browser walkthrough.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: generated TypeScript contracts are up to date.

What is happening: the workflow client contract is compared with backend schema generation.

Why this matters: the browser must accept nullable empty workflow state and live metadata.

```bash
cd frontend/admin
npm run typecheck
npm test -- --run src/components/workflows/WorkflowBuilderPage.test.tsx src/components/workflows/WorkflowGraphPanel.test.tsx src/components/workflows/WorkflowReferencePicker.test.tsx src/components/workflows/WorkflowPublishPanel.test.tsx src/components/workflows/WorkflowSectionForm.test.tsx src/components/workflows/WorkflowValidationPanel.test.tsx src/components/workflows/WorkflowRevisionPanel.test.tsx
npm run build
cd ../..
```

Expected: workflow typecheck, tests, and build pass.

What is happening: the React workflow workspace is validated outside the browser walkthrough.

Why this matters: screenshots alone cannot prove the generated client and component contracts remain strict.

```bash
uv run pytest --no-cov tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_platform_tenant_and_auth0_are_safe tests/integration/test_admin_react_routes.py::test_react_admin_workflow_builder_save_validate_and_publish_paths tests/integration/api/test_admin_workflow_ui.py tests/integration/api/test_admin_workflows_api.py tests/contract/test_admin_react_contract.py tests/unit/api/test_admin_workflow_builder_schema.py tests/unit/api/test_workflow_builder_schemas.py tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/workflows/test_workflow_builder_queries.py -q
```

Expected: focused backend workflow coverage passes.

What is happening: workflow route, service, schema, scanner, and performance checks validate browser assumptions.

Why this matters: UI evidence must be backed by executable backend behavior.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: full lint, format, type, and coverage gates pass before release approval.

What is happening: qa050 is checked against the broader repository gates.

Why this matters: workflow live-data work touches shared React contracts and FastAPI route policy.

## UI Evidence Checklist

- The empty workflow page has no fixed Spec 030 workflow rows.
- The seeded workflow page reflects durable API data.
- Save or validation uses backend actions and returns safe audit/reference summaries.
- Publish readiness reflects live evidence and blockers.
- Cross-tenant access fails closed.
- Browser evidence and API evidence do not contain raw secrets or unsafe payloads.

## Acceptance Notes Template

Save this summary as `/tmp/qa050-ui-acceptance-notes.txt`.

```text
QA ID: qa050
Reviewer principal: tenant-admin-acme
Empty workflow screenshot: /tmp/qa050-ui-workflows-empty.png
Seeded workflow screenshot: /tmp/qa050-ui-workflows-seeded.png
Save action screenshot: /tmp/qa050-ui-workflow-save.png
Publish gate screenshot: /tmp/qa050-ui-publish-gate.png
Post-UI API notes: /tmp/qa050-ui-post-api-notes.txt
Cross-tenant negative result: denied
Redaction review: passed
```

Expected: every evidence item exists before manual UI approval.

What is happening: the reviewer creates a compact browser evidence index.

Why this matters: qa050 acceptance depends on both visual and API-backed evidence.

## Troubleshooting

- If the workflow page stays on loading, check the browser console and `/admin/app/workflows/builder.json` response.
- If local login does not list `tenant-admin-acme`, confirm `.env.qa050` was copied before starting the API.
- If the empty state is missing, reset the qa050 database and rerun migrations without workflow seed helpers.
- If seeded data is missing, rerun the focused workflow route test or the Spec QA seed step.
- If save does not produce a visible mutation result, inspect the save POST response and confirm the current revision token matches the draft.
- If cross-tenant access leaks Acme details, stop validation and fix authorization before continuing.

Expected: troubleshooting isolates UI, auth, seed, and authorization failures safely.

What is happening: reviewers can recover from common local QA setup problems.

Why this matters: validation should stop only for real blockers, not ambiguous setup gaps.

## Related Files

- `specs/050-workflow-react-live-data/qa050.md`
- `specs/050-workflow-react-live-data/qa050_user_guide.md`
- `specs/050-workflow-react-live-data/.env.qa050`
- `specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml`
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- `frontend/admin/src/components/workflows/WorkflowRegistryPage.tsx`
- `frontend/admin/src/api/client.ts`
- `src/multi_agent_platform/api/routers/admin_react.py`
