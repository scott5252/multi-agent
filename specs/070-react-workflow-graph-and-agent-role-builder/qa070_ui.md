# QA070 UI: React Workflow Graph And Agent Role Builder

## Goal
This browser-first guide helps a non-developer reviewer validate the Spec 070 workflow graph and role builder.
The reviewer uses local-principal login, visible Workflow Registry navigation, form controls, buttons, graph canvas, and list alternatives.
The reviewer does not edit raw JSON.
The reviewer does not call backend APIs to configure the workflow.
API and command checks are listed only as supporting evidence.

## How To Use This Guide
Run the setup commands from the repository root.
Use a fresh browser session if possible.
Capture screenshots under `/tmp/qa070-*` or keep the Playwright screenshots under `output/playwright/qa070_ui`.
Read each Expected line before moving to the next action.
Use the What is happening and Why this matters notes to distinguish expected behavior from regressions.
Stop if protected data appears in the UI.
Stop if a cross-tenant user can see Acme workflow data.

## Environment Setup
```bash
cp specs/070-react-workflow-graph-and-agent-role-builder/.env.qa070 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa070 && createdb -U postgres multi_agent_platform_qa070'
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_graph_role_builder_qa070.py
```
Expected: the seed command prints `70707070-6669-4670-8670-000000000070`.
What is happening: the QA database receives one Acme workflow draft with three agent roles and a join node.
Why this matters: the browser journey starts from deterministic durable state.

```bash
mkdir -p /tmp/qa070-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa070-ui/server.log 2>&1 &
sleep 2
curl --fail --silent http://127.0.0.1:8000/health/live
```
Expected: the health check exits 0.
What is happening: the local FastAPI app is serving React Admin assets and JSON routes.
Why this matters: the reviewer can validate the browser UI without a production system.

```bash
cd frontend/admin && npm run build
```
Expected: the React build exits 0.
What is happening: the admin assets compile with the graph/role editor.
Why this matters: the served UI matches production build expectations.

## Browser Walkthrough
1. Open local login.
Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`
Navigation path: direct local login entrypoint, then visible Admin workflow page.
Action: choose `tenant-admin-acme`.
Expected: the browser opens Workflow Registry and shows `QA070 Graph Role Builder`.
What is happening: local-principal auth creates an Acme tenant admin session.
Why this matters: all later workflow setup actions run under tenant-scoped authorization.

2. Review the Workflow Registry area.
Page URL: `http://127.0.0.1:8000/admin/app/workflows`
Navigation path: Admin shell, Workflow Registry.
Action: inspect the registry list and create panel.
Expected: the seeded workflow appears and no fake workflows are invented.
What is happening: the UI reads durable workflow registry data.
Why this matters: truthful empty/live states are required for workflow setup.

3. Review the section rail.
Action: inspect Metadata, Roles, References, Contracts, Graph, Joins, Approvals, Subworkflows, Tests, Annotations, and Publish links.
Expected: section labels show backend-owned status badges and safe summaries.
What is happening: the builder renders section summaries from the backend envelope.
Why this matters: validation and readiness are not guessed by the browser.

4. Edit metadata.
Action: change the Name field to `QA070 Graph Role Builder Browser Check`.
Expected: the dirty state changes to `Unsaved changes`.
What is happening: the local document projection updates display name and description fields.
Why this matters: dirty state lets reviewers see unsaved browser edits before persistence.

5. Review role controls.
Action: inspect Coordinator, Research agent, and Review agent role cards.
Expected: each role has key, name, kind, contract selectors, profile reference, prompt refs, skill refs, purpose, responsibilities, duplicate, move, and delete controls.
What is happening: role definitions are editable as structured fields.
Why this matters: custom workflow agents can be authored without raw JSON.

6. Add an agent role.
Action: click `Add role`.
Expected: a `New agent` card appears.
What is happening: the browser adds a safe role item to the local workflow document.
Why this matters: the reviewer can create a new agent role through a visible control.

7. Review dependency warnings.
Action: look at the Coordinator role card.
Expected: it shows node references such as `Referenced by node start`.
What is happening: the UI presents advisory dependency warnings for visible references.
Why this matters: users are warned before deleting referenced records, while backend validation remains authoritative.

8. Review contract controls.
Action: inspect Request, Result, and Approval decision contract cards.
Expected: each card exposes key, name, kind, schema type, producers, consumers, version, and compatibility notes.
What is happening: contracts are editable through guided form controls.
Why this matters: workflow inputs, outputs, and approval decisions are explicit contracts.

9. Add a contract.
Action: click `Add contract`.
Expected: a `New contract` card appears and the page remains stable.
What is happening: the browser adds a safe contract item to local state.
Why this matters: users can author data contracts without raw JSON schema editing.

10. Review graph topology controls.
Action: inspect Entry node, Nodes, and Edges.
Expected: role nodes, join node, approval node, terminal node, edge selectors, branch labels, contract selectors, and layout number fields are visible.
What is happening: topology is represented as form/list controls.
Why this matters: keyboard users have equivalent editing controls for the graph.

11. Review join controls.
Action: inspect the Evidence join policy.
Expected: strategy `quorum`, inbound edges, required branches, quorum, timeout, failure behavior, and output contract controls are visible.
What is happening: coordination behavior is editable as durable join policy data.
Why this matters: multi-agent branch convergence can be configured without direct API calls.

12. Review approval controls.
Action: inspect Manager approval.
Expected: key, name, approver scope, decision contract, resume behavior, and instructions controls are visible.
What is happening: approval gates are durable workflow document entries.
Why this matters: human approval remains persistent state.

13. Review subworkflow controls.
Action: click `Add subworkflow`.
Expected: a `New subworkflow` card appears with alias, name, version reference, and contract selectors.
What is happening: the editor creates an authorized-reference placeholder.
Why this matters: users can prepare subworkflow references without exposing unauthorized tenant data.

14. Review the graph canvas.
Action: scroll to Workflow structure.
Expected: the canvas is nonblank and shows nodes connected by edges.
What is happening: `@xyflow/react` renders the dirty workflow document projection.
Why this matters: visual graph review updates as users edit the document.

15. Review keyboard-readable graph lists.
Action: inspect Nodes and Edges and joins lists under the canvas.
Expected: list counts and labels match the graph canvas.
What is happening: the same graph projection is rendered as text.
Why this matters: the canvas is not the only way to understand graph state.

16. Save the draft.
Action: click `Save draft`.
Expected: a safe `Draft saved` mutation result appears.
What is happening: the UI submits the full workflow document through the backend save route.
Why this matters: durable persistence, idempotency, stale checks, validation, and audit stay server-owned.

17. Reload the page.
Action: use browser reload.
Expected: `New agent` remains visible.
What is happening: the saved role is loaded from the workflow draft revision.
Why this matters: edits survive browser reload and are not transient UI-only state.

18. Run backend validation from the UI.
Action: click `Run validation`.
Expected: backend-owned findings refresh and show safe section links if blockers exist.
What is happening: validation is requested from the server.
Why this matters: publish readiness must not rely on browser-only graph checks.

19. Check stale recovery display.
Action: click `Simulate stale save`.
Expected: stale conflict messaging appears with a safe reload path.
What is happening: the UI exercises the stale-save branch without overwriting newer revisions.
Why this matters: stale browser tabs must not mutate durable workflow state.

20. Check mobile layout.
Action: resize the browser to about 390 pixels wide or use Playwright mobile screenshot.
Expected: sections become single-column, controls remain usable, and text does not overlap.
What is happening: responsive CSS constrains fixed-format controls and graph framing.
Why this matters: workflow setup must remain usable on narrow viewports.

21. Check cross-tenant denial.
Action: log out or open local login again and choose `tenant-admin-globex`, then navigate to Workflow Registry.
Expected: Acme `QA070 Graph Role Builder` draft is not visible.
What is happening: tenant scope changes to Globex.
Why this matters: cross-tenant workflow setup access fails closed.

22. Check redaction.
Action: scan visible UI, screenshots, and `/tmp/qa070-ui/server.log`.
Expected: no raw secrets, credentials, provider headers, raw prompts outside edit forms, completions, memory contents, raw run payloads, private messages, raw tool payloads, raw test transcripts, stack traces, or local filesystem paths appear.
What is happening: UI and logs display safe summaries only.
Why this matters: workflow setup must not become a leak path.

## Required Automated Evidence
```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```
Expected: generated TypeScript contracts are fresh.
What is happening: generated client types still match backend schemas.
Why this matters: the editor consumes backend-owned contracts.

```bash
uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py -q --no-cov
```
Expected: focused backend tests pass.
What is happening: route contracts and rich document persistence are validated.
Why this matters: UI saves must round-trip through durable backend services.

```bash
cd frontend/admin && npm test -- Workflow
```
Expected: workflow component tests pass.
What is happening: React helpers, controls, graph projection, and save payload assembly are tested.
Why this matters: browser behavior is covered before manual review.

```bash
cd frontend/admin && npm run typecheck
cd frontend/admin && npm run build
```
Expected: TypeScript and build pass.
What is happening: strict frontend compilation validates component contracts.
Why this matters: the workflow setup UI is production-buildable.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
Expected: repository gates pass.
What is happening: global quality checks run after the UI change.
Why this matters: Spec 070 must not regress broader platform quality.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml --start-processes
```
Expected: `qa070-workflow-graph-role-desktop.png` and `qa070-workflow-graph-role-mobile.png` are created.
What is happening: Playwright logs in, exercises the editor, saves, reloads, and captures two viewports.
Why this matters: desktop and mobile evidence is required before Spec 071 begins.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/070-react-workflow-graph-and-agent-role-builder
```
Expected: QA docs validation passes.
What is happening: guide, UI walkthrough, and environment file are checked.
Why this matters: manual reviewers need complete instructions.

## UI Evidence Checklist
Capture `/tmp/qa070-ui/workflow-registry.png`.
Capture `/tmp/qa070-ui/roles-editor.png`.
Capture `/tmp/qa070-ui/contracts-editor.png`.
Capture `/tmp/qa070-ui/topology-editor.png`.
Capture `/tmp/qa070-ui/join-approval-editor.png`.
Capture `/tmp/qa070-ui/graph-canvas-desktop.png`.
Capture `/tmp/qa070-ui/graph-canvas-mobile.png`.
Record that `New agent` persisted after reload.
Record that backend validation findings link to safe sections.
Record that cross-tenant Globex does not show Acme workflow labels.
Record that no protected raw material appears in screenshots.

## Acceptance Notes Template
Reviewer:
Date:
Branch:
QA database:
Browser:
Desktop screenshot path:
Mobile screenshot path:
Save result:
Validation result:
Cross-tenant result:
Redaction scan result:
Notes:

## Troubleshooting
If the login page does not show local principals, confirm `.env.qa070` was copied to `.env`.
If the workflow is missing, rerun `uv run python scripts/qa/seed_workflow_graph_role_builder_qa070.py`.
If the page shows an empty state, verify the browser is logged in as `tenant-admin-acme`.
If save fails with stale conflict, reload the page and retry from current revision.
If save fails with validation errors after manual edits, inspect the field path and return to the named section.
If the graph canvas is blank, check that the Nodes list has entries and keep the screenshot.
If mobile controls overlap, capture the viewport dimensions and screenshot.
If Playwright fails to click a button, confirm the API server is running and the seed data exists.
If cross-tenant data appears, stop the QA run and preserve evidence.
If protected data appears, stop the QA run and preserve evidence.

## Related Files
- `specs/070-react-workflow-graph-and-agent-role-builder/qa070.md`
- `specs/070-react-workflow-graph-and-agent-role-builder/qa070_user_guide.md`
- `specs/070-react-workflow-graph-and-agent-role-builder/.env.qa070`
- `scripts/qa/seed_workflow_graph_role_builder_qa070.py`
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- `frontend/admin/src/components/workflows/WorkflowRoleEditor.tsx`
- `frontend/admin/src/components/workflows/WorkflowContractEditor.tsx`
- `frontend/admin/src/components/workflows/WorkflowTopologyEditor.tsx`
- `frontend/admin/src/components/workflows/WorkflowJoinApprovalEditor.tsx`
- `frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx`
- `frontend/admin/src/components/workflows/workflowDocumentEditor.ts`
- `specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml`
