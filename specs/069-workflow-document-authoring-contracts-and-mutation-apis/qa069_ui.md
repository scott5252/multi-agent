# QA069 UI Walkthrough: Workflow Document Authoring Contracts And Mutation APIs

## Goal
This qa069 UI walkthrough verifies that a reviewer can use the React Admin workflow page to exercise the full document authoring contract without a raw JSON editor.
The UI should load the seeded workflow draft, display safe section summaries, show revision context, send a full document payload on save, and render safe mutation results.
The walkthrough uses local-principal login at `http://127.0.0.1:8000/auth/local-login`.
The expected primary route is `/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111`.

## How To Use This Guide
Run the setup commands first, then follow the browser steps in order.
Keep screenshots under `output/playwright/qa069_ui` or `/tmp/qa069-ui-*`.
Use browser developer tools only to confirm request shape and response status; do not paste raw protected payloads into notes.
Every step includes Expected, What is happening, and Why this matters lines.
Stop the walkthrough if a stack trace, secret-like value, raw prompt body, raw completion, provider payload, raw tool payload, private message, memory content, or local filesystem path appears.

## Environment Setup
```bash
cp specs/069-workflow-document-authoring-contracts-and-mutation-apis/.env.qa069 .env
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_document_authoring_qa069.py
```
Expected: the seed script prints the QA069 workflow draft ID.
What is happening: the database is prepared with deterministic Acme workflow authoring data.
Why this matters: the browser checks need a real durable draft, not a mock row.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa069-ui-api.log 2>&1 &
cd frontend/admin && npm run build
```
Expected: the API starts and the React Admin build succeeds.
What is happening: FastAPI will serve the built React assets and JSON routes.
Why this matters: reviewers test the same browser route family used by the app.

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
```
Expected: the health check exits 0.
What is happening: the local API is reachable before browser work starts.
Why this matters: browser failures are easier to diagnose when server readiness is known.

## Browser Walkthrough
### Step 1: Open Local Login
Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111`.
Expected: the local-principal login page shows an option for `tenant-admin-acme`.
What is happening: the local auth mode is exercising tenant admin authorization without Auth0.
Why this matters: QA uses deterministic principals while preserving authorization checks.

### Step 2: Select Acme Tenant Admin
Click the `tenant-admin-acme` login button.
Expected: the browser lands on the React Admin workflow page and visible text includes `Workflow`.
What is happening: a local principal cookie is set and the React shell resolves Acme scope.
Why this matters: the workflow document editor must be scoped to the authorized tenant.

### Step 3: Confirm Registry And Builder Load
Confirm the workflow registry section is visible.
Confirm the builder section shows a draft revision.
Confirm section status badges are visible.
Expected: the page contains workflow registry content, revision text, and authoring controls.
What is happening: React loaded `/admin/app/workflows/builder.json` and projected durable workflow state.
Why this matters: the full document contract starts at editor load, not only at save.

### Step 4: Inspect Safe Draft Facts
Read the draft facts for revision, lineage, scope, and section count.
Expected: revision is visible, the lineage is a UUID, scope is tenant-oriented, and section count is positive.
What is happening: the backend is returning safe metadata summaries.
Why this matters: the UI can guide users without exposing raw workflow payloads.

### Step 5: Edit Metadata
Change the Name field to `QA069 Workflow Document UI Save`.
Change the Description field to `Saved through QA069 browser walkthrough`.
Expected: the unsaved changes indicator appears.
What is happening: React updates local form state while keeping the loaded document as the save base.
Why this matters: metadata edits must become part of the complete document payload.

### Step 6: Save Draft
Click `Save draft`.
Expected: the mutation result status is `accepted` and an audit reference appears.
What is happening: the browser sends revision, idempotency key, safe client context, metadata, and the complete document.
Why this matters: Spec 069 closes the previous gap where React saves only changed metadata.

### Step 7: Confirm Document Request Shape
Open the browser Network panel and inspect the save request body.
Expected: the request contains `document.workflow_key`, `document.roles`, `document.nodes`, `document.edges`, `revision`, and `idempotency_key`.
What is happening: the generated TypeScript client is carrying the full authoring document contract.
Why this matters: later graph and prompt/profile controls need this contract to preserve all sections.

### Step 8: Confirm Safe Result Shape
Inspect the save response body.
Expected: the response contains `status`, `revision`, `validation`, and may contain `editor_state`.
What is happening: the backend returns a mutation result rather than raw database rows.
Why this matters: the UI can update from safe durable state after the save.

### Step 9: Simulate Stale Save
Click `Simulate stale save`.
Expected: the mutation result status changes to `stale conflict` or shows safe reload guidance.
What is happening: the UI submits a stale revision token and the backend rejects the write.
Why this matters: stale tabs must never overwrite newer workflow draft revisions.

### Step 10: Review Validation Panel
Scroll to the validation panel.
Expected: validation findings, if present, show section labels, safe messages, and recommended action text.
What is happening: backend-owned validation summaries are rendered as actionable UI content.
Why this matters: invalid full documents need field-oriented feedback that is safe for browser display.

### Step 11: Redaction Sweep
Search visible page text for `raw prompt`, `raw completion`, `provider payload`, `tool payload`, `credential`, `stack trace`, and `/Users/`.
Expected: none of those terms appear.
What is happening: the browser is rendering safe summaries and references only.
Why this matters: workflow authoring must not leak protected runtime or credential material.

### Step 12: Capture Evidence
Save a full-page screenshot to `output/playwright/qa069_ui/manual-workflow-document-save.png`.
Expected: the screenshot shows the workflow page, authoring form, and safe mutation result without protected raw markers.
What is happening: the reviewer captures durable evidence for the browser workflow.
Why this matters: QA review can verify UI behavior without rerunning the session.

## Required Automated Evidence
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
Expected: backend quality commands exit 0.
What is happening: repository quality gates run against the implementation.
Why this matters: UI behavior is not complete if backend contracts fail quality gates.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
cd frontend/admin && npm run typecheck
cd frontend/admin && npm test
cd frontend/admin && npm run build
```
Expected: generated types are fresh and frontend checks exit 0.
What is happening: TypeScript validates the full document save request and result contracts.
Why this matters: the UI depends on generated backend contracts.

```bash
cd frontend/admin && npm test -- Workflow
```
Expected: workflow component tests pass.
What is happening: the builder, section form, validation panel, graph panel, and related workflow components are tested together.
Why this matters: the UI can send the full document and render new result fields.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml --start-processes
```
Expected: Playwright writes `qa069-workflow-setup-smoke.png`.
What is happening: the browser logs in through local-principal auth and opens workflow UI.
Why this matters: automated evidence covers the same route a manual reviewer sees.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/069-workflow-document-authoring-contracts-and-mutation-apis
```
Expected: QA doc validation passes.
What is happening: this walkthrough, the API guide, and `.env.qa069` meet reviewer evidence requirements.
Why this matters: incomplete QA docs block Spec Kit validation.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml
```
Expected: Spec QA exits 0.
What is happening: manifest-driven backend, frontend, and documentation checks run together.
Why this matters: Spec 069 cannot hand off to Spec 070 until validation is green.

## UI Evidence Checklist
- Browser URL starts with `http://127.0.0.1:8000/admin/app/workflows`.
- Principal is `tenant-admin-acme`.
- Visible scope is Acme tenant.
- Draft revision appears before save.
- Section summaries or section badges are visible.
- Save button sends a request with `document`.
- Accepted save result is visible.
- Stale save result is visible after simulation.
- Validation panel shows safe field-oriented messages.
- Screenshot path is recorded.
- No protected raw markers appear in page text.

## Acceptance Notes Template
- Date:
- Reviewer:
- Browser:
- Login principal:
- Screenshot path:
- Save request contained document:
- Save result status:
- Stale result status:
- Validation panel reviewed:
- Redaction sweep result:
- Notes:

## Troubleshooting
If login loops, clear the `map_local_principal` cookie and reload the local login page.
If the workflow page is empty, rerun the QA069 seed script and confirm the Acme tenant ID.
If the save button is disabled, change the Name or Description field to create dirty state.
If stale simulation reports accepted, reload the page and verify the current revision changed after the first save.
If the Network panel does not show `document`, rerun generated type checks and rebuild frontend assets.
If screenshot output is blank, rerun Playwright with `--start-processes` and inspect `/tmp/qa069-ui-api.log`.
If raw protected markers appear, stop and file a redaction defect.

## Related Files
- `specs/069-workflow-document-authoring-contracts-and-mutation-apis/qa069.md`
- `specs/069-workflow-document-authoring-contracts-and-mutation-apis/.env.qa069`
- `scripts/qa/seed_workflow_document_authoring_qa069.py`
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- `frontend/admin/src/components/workflows/WorkflowSectionForm.tsx`
- `frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx`
- `frontend/admin/src/api/generated/reactAdminApi.ts`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/admin/workflow_builder.py`
